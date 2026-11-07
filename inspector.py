#!/usr/bin/env python3
"""Offline QNX 8 build and timing evidence inspector. Python 3.10+, stdlib only."""
import argparse
import csv
import hashlib
import html
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
TARGETS = {'x86_64': ('gcc_ntox86_64', 62), 'aarch64': ('gcc_ntoaarch64le', 183)}
LIMIT = 8 * 1024 * 1024


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def elf_info(path, target):
    with open(path, 'rb') as f:
        data = f.read(64)
    if len(data) < 64 or data[:4] != b'\x7fELF' or data[4:7] != b'\x02\x01\x01':
        raise ValueError('Expected a complete little-endian ELF64 header')
    kind, machine, version = struct.unpack_from('<HHI', data, 16)
    if kind not in (2, 3) or version != 1 or machine != TARGETS[target][1]:
        raise ValueError('ELF executable architecture/type does not match selected QNX target')
    return {'machine': machine, 'target': target, 'sha256': digest(path),
            'limitation': 'ELF architecture alone does not prove QNX origin or runtime compatibility.'}


def read_text(path):
    with open(path, 'rb') as f:
        data = f.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('Input exceeds 8 MiB limit')
    return data.decode('utf-8')


def analyze(path, budget):
    text = read_text(path)
    lines = text.splitlines()
    if not lines:
        raise ValueError('Empty capture')
    meta = json.loads(lines[0])
    if not isinstance(meta, dict) or meta.get('schema') != 'qnx-probe-v1':
        raise ValueError('Unknown probe schema')
    if meta.get('sysname') != 'QNX' or not re.fullmatch(r'8\.0(?:\.[0-9]+)*', str(meta.get('release', ''))):
        raise ValueError('Capture must identify QNX OS 8.0')
    if meta.get('clock_api') != 'clock_gettime_mon_ns' or meta.get('machine') not in ('x86_64', 'aarch64', 'aarch64le'):
        raise ValueError('Unexpected QNX clock API or architecture')
    for field in ('period_ns', 'samples', 'clock_period_ns'):
        if type(meta.get(field)) is not int or meta[field] <= 0:
            raise ValueError('Invalid metadata: ' + field)
    if meta['samples'] > 100000:
        raise ValueError('Too many samples')
    rows = csv.DictReader(io.StringIO('\n'.join(lines[1:])))
    if rows.fieldnames != ['sample', 'scheduled_ns', 'actual_ns']:
        raise ValueError('Unexpected CSV columns')
    lateness = []
    previous = None
    previous_actual = None
    for i, row in enumerate(rows):
        if i >= meta['samples'] or None in row or any(v is None for v in row.values()):
            raise ValueError('Malformed or excess rows')
        n, scheduled, actual = (int(row[k]) for k in rows.fieldnames)
        if n != i or not 0 < scheduled <= actual < 2**64:
            raise ValueError('Invalid sequence or timestamps')
        if previous is not None and (scheduled - previous != meta['period_ns'] or actual < previous_actual):
            raise ValueError('Non-monotonic timestamps or inconsistent period')
        lateness.append(actual - scheduled)
        previous, previous_actual = scheduled, actual
    if len(lateness) != meta['samples']:
        raise ValueError('Truncated capture: sample count mismatch')
    ordered = sorted(lateness)
    return {'metadata': meta, 'capture_sha256': digest(path), 'samples': len(ordered),
            'lateness_ns': {'min': ordered[0], 'median': ordered[(len(ordered)-1)//2],
                            'p99': ordered[math.ceil(len(ordered)*.99)-1], 'max': ordered[-1]},
            'budget_ns': budget, 'over_budget': sum(v > budget for v in ordered),
            'provenance': 'Imported operator-supplied capture; not authenticated target attestation.',
            'limitation': 'Observed wake-up lateness, not a worst-case latency guarantee.'}


def run(argv):
    # No shell interpretation; output is bounded through temporary files.
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            p = subprocess.run(argv, stdout=out, stderr=err, timeout=60, check=False)
            code = p.returncode
        except subprocess.TimeoutExpired:
            code = 124
        out.seek(0); err.seek(0)
        return {'argv': argv, 'returncode': code,
                'stdout': out.read(LIMIT).decode(errors='replace'),
                'stderr': err.read(LIMIT).decode(errors='replace')}


def doctor():
    compiler = shutil.which('qcc')
    env = {key: bool(os.environ.get(key)) and Path(os.environ[key]).is_dir()
           for key in ('QNX_HOST', 'QNX_TARGET')}
    return {'qcc': compiler, 'environment_directories_present': env,
            'ready_for_build_attempt': bool(compiler) and all(env.values()),
            'next_step': 'Load the SDP 8.0 qnxsdp-env.sh environment, then build. SDK version is enforced by the probe compile guard.'}


def write_report(data, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    data['generated_utc'] = datetime.now(timezone.utc).isoformat()
    body = json.dumps(data, indent=2)
    (directory / 'report.json').write_text(body + '\n')
    (directory / 'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>QNX Evidence Inspector</title><style>body{background:#101923;color:#e8f0fa;'
        'font:18px system-ui;margin:40px auto;max-width:1000px;padding:0 20px}h1{color:#70e0cb}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#192737;padding:24px;border-radius:12px}'
        '</style><h1>QNX Build &amp; Evidence Inspector</h1><p>Observed results and explicit limitations</p><pre>'
        + html.escape(body) + '</pre></html>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    build = sub.add_parser('build')
    build.add_argument('--target', choices=TARGETS, default='x86_64')
    build.add_argument('--out', default='build')
    inspect = sub.add_parser('inspect')
    inspect.add_argument('binary'); inspect.add_argument('--target', choices=TARGETS, default='x86_64')
    analysis = sub.add_parser('analyze')
    analysis.add_argument('capture'); analysis.add_argument('--budget-ns', type=int, default=1000000)
    analysis.add_argument('--out', default='report')
    args = parser.parse_args(argv)
    try:
        if args.command == 'doctor':
            data = doctor(); print(json.dumps(data, indent=2))
            return 0 if data['ready_for_build_attempt'] else 2
        if args.command == 'inspect':
            print(json.dumps(elf_info(args.binary, args.target), indent=2)); return 0
        if args.command == 'analyze':
            if args.budget_ns < 0:
                raise ValueError('Budget must be nonnegative')
            data = analyze(args.capture, args.budget_ns)
            write_report(data, args.out)
            print(json.dumps(data, indent=2))
            return 3 if data['over_budget'] else 0
        directory = Path(args.out).resolve(); directory.mkdir(parents=True, exist_ok=True)
        data = {'environment': doctor(), 'build_verified': False, 'runtime_verified': False}
        if not data['environment']['ready_for_build_attempt']:
            write_report(data, directory)
            print('QNX SDK environment missing; build NOT verified.', file=sys.stderr); return 2
        source = ROOT / 'probe' / 'timing_probe.c'
        binary = directory / 'timing-probe'
        if binary.exists():
            binary.unlink()  # Prevent stale output from becoming build evidence.
        data['source_sha256'] = digest(source)
        data['compiler_listing'] = run([data['environment']['qcc'], '-V'])
        data['compile'] = run([data['environment']['qcc'], '-V'+TARGETS[args.target][0],
                               '-std=c11', '-D_QNX_SOURCE', '-Wall', '-Wextra', '-Werror',
                               '-O2', str(source), '-o', str(binary)])
        if data['compile']['returncode'] == 0:
            try:
                data['binary'] = elf_info(binary, args.target)
                data['build_verified'] = True
            except (OSError, ValueError) as e:
                data['error'] = str(e)
        write_report(data, directory)
        print(json.dumps(data, indent=2))
        return 0 if data['build_verified'] else 2
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as e:
        print('Error: ' + str(e), file=sys.stderr); return 2


if __name__ == '__main__':
    sys.exit(main())
