# QNX Build & Evidence Inspector

A dependency-free host tool for building a QNX OS 8.0 timing probe, checking target architecture, and analyzing captured wake-up lateness. Category: **Developer Tooling & Host Tools**.

Sponsored by CREIGNIFICENT LLC.

## Verified status

Implemented: Python CLI, QNX-targeted C probe, ELF architecture validation, strict capture parser, JSON/HTML reports, host tests, and CI workflow.

**15 host tests passed on Linux on November 7, 2026. QNX compilation and target execution have NOT been verified.** The SDK is unavailable in the development workspace. See `evidence/local-sdk-check/report.json`. Windows/macOS CI is configured but has not been run here. Public repository: https://github.com/CreigT/qnx-evidence-inspector. No demonstration video has been published.

## What problem it solves

A developer can accidentally compile for the host, use the wrong target architecture, analyze a truncated timing log, or mistake a successful host test for a successful QNX run. This tool checks these distinct stages and keeps the limitations in its reports.

It is an original host tool, not a port of an upstream project. No paid API, cloud service, Python package installation, or AI model is required.

## Requirements

- Host: Python 3.10+; Linux is the locally tested host. Python-only inspection/analysis also targets Windows and macOS.
- Cross-build: licensed QNX SDP 8.0 with `qcc`, QNX target headers and libraries, on a host supported by that SDK.
- Runtime target: QNX OS 8.0, x86_64 QEMU guest (primary intended target), or a supported AArch64 device.
- Obtain SDK and target image through [QNX Everywhere](https://www.qnx.com/developers/docs/qnxeverywhere/). This repository does not redistribute QNX binaries, licenses, or boot images. Follow the supplied image's QEMU launch instructions; disk, firmware and machine options depend on the image.

## 1. Run the host checks

From this repository directory:

```sh
python3 -m unittest discover -s tests -v
python3 inspector.py doctor
```

On Windows use `python` if `python3` is unavailable. Doctor exits 2 if qcc or environment directories are missing. This is a diagnostic result, not a Python crash.

## 2. Build the QNX probe

On your SDP-supported host, load the environment script from your actual SDP 8.0 installation. For a Linux installation at `$HOME/qnx800`:

```sh
. "$HOME/qnx800/qnxsdp-env.sh"
python3 inspector.py doctor
python3 inspector.py build --target x86_64 --out build/x86_64
python3 inspector.py inspect build/x86_64/timing-probe --target x86_64
```

For AArch64 use `--target aarch64` and a separate output directory. The exact cross-build is recorded in `report.json`. Equivalent x86_64 compiler invocation:

```sh
qcc -Vgcc_ntox86_64 -std=c11 -D_QNX_SOURCE -Wall -Wextra -Werror -O2 probe/timing_probe.c -o timing-probe
```

The probe requires QNX headers, enforces `_NTO_VERSION` 800–809, and links QNX-specific functions. The build report saves source and binary SHA-256 hashes, compiler listing, command arguments, compiler output, and architecture. A successful compile plus architecture check means `build_verified: true`; it never sets `runtime_verified` to true. These results trust your local compiler and environment.

## 3. Capture a target run

Boot your QNX OS 8.0 x86_64 image using its documented QEMU launcher. Transfer the binary using the image's supported mechanism (SCP if SSH is enabled, otherwise shared storage or your development tools). Do not execute the QNX binary on the Linux host.

On the QNX target, from a writable directory:

```sh
uname -a
chmod +x timing-probe
./timing-probe > capture.csv
```

The capture takes about 10 seconds: 1,000 scheduled wakes, 10 milliseconds apart. It buffers samples before printing to avoid console I/O inside the measurement loop. Transfer `capture.csv` back to the host, preserving its contents. Record the image version, hardware/QEMU version and launch command, CPU allocation, scheduling policy, background load, and target `uname -a` in your evidence notes.

## 4. Analyze and share

```sh
python3 inspector.py analyze capture.csv --budget-ns 1000000 --out report
```

Open `report/report.html` in a browser, or inspect `report/report.json`. The example budget is 1 millisecond of wake-up lateness, **not** a certification threshold. Choose a budget appropriate to your experiment.

Outputs include minimum, lower median, nearest-rank p99, maximum wake-up lateness, and count strictly above budget. Exit codes: 0 success/within budget; 2 missing prerequisites or invalid input/build failure; 3 valid capture with over-budget samples. Reports are still written on budget failure.

## Meaningful QNX connection

| File/function | QNX connection |
| --- | --- |
| `probe/timing_probe.c` | Includes `<sys/neutrino.h>`; compile guard rejects non-QNX or non-8.0 headers. |
| `ClockPeriod()` | Reads QNX clock period without changing system settings. |
| `clock_gettime_mon_ns()` | QNX nanosecond monotonic clock API used for each actual wake time. |
| `inspector.py:main` build path | Invokes QNX `qcc` variants `gcc_ntox86_64` / `gcc_ntoaarch64le`. |
| `inspector.py:analyze` | Validates and analyzes the probe's QNX 8.0 capture schema. |

## Limits and trust boundaries

This is a developer diagnostic, not a safety system, schedulability proof, or worst-case execution-time analyzer. QEMU timing reflects the host scheduler and virtualization. Do not generalize these observations to medical or vehicle safety.

Captures are operator-supplied and can be forged; schema checks and hashes are not remote attestation. An ELF header can confirm architecture but cannot prove a QNX origin. The build path adds compiler/source evidence, but trusts the selected `qcc`. The tool does not inspect arbitrary ELF sections or dependencies and cannot certify arbitrary applications as QNX-compatible.

No shell is used to execute the compiler. Compiler calls have 60-second timeouts and retained output limits; this is not a resource sandbox for untrusted compilers. Input captures are capped at 8 MiB and 100,000 samples. Generated HTML escapes input and loads no scripts or external assets. Build/report commands overwrite their selected output files; choose dedicated output directories. Review compiler logs for local paths before publishing.

## Documentation

- [Submission description](docs/SUBMISSION.md)
- [Demo script](docs/DEMO.md)
- [Hands-on codelab](docs/CODELAB.md)
- [Validation record](evidence/VALIDATION.md)
- [QNX qcc documentation](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/q/qcc.html)
- [QNX clock API documentation](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/clock_gettime_ns.html)
- [QNX ClockPeriod documentation](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/c/clockperiod.html)

## SECURE

- Host tests and architecture checks are distinct from QNX runtime verification. Reports never claim runtime success from host checks alone.
- Captures are operator-supplied; schema and hash checks are not remote attestation.
- No shell is used to invoke the compiler. Timeouts and output limits are applied.
- The tool does not execute QNX binaries on the host.
- Input size is capped. Generated HTML escapes content.

## VERIFY

Verification is evidence of host tooling behavior and explicit limitations, not QNX target certification.

- Host unit tests pass.
- Reports distinguish build/architecture evidence from runtime verification.
- Invalid or truncated captures are rejected or flagged.
- No host execution of the target binary occurs.

See `docs/VERIFY_WALKTHROUGH.md` for the concrete steps. Full operational card: `docs/OPERATIONAL_CARD.md`.

## DOCUMENT

- Operational card: `docs/OPERATIONAL_CARD.md`
- Verification walkthrough: `docs/VERIFY_WALKTHROUGH.md`
- Existing docs and evidence records remain unchanged.
- Documentation defines the verified host boundary; QNX target results require separate evidence.

MIT licensed. QNX is referenced only to identify the supported platform; this project is not endorsed by QNX.
