# Submission draft — update verification status before submitting

**Project:** QNX Build & Evidence Inspector

**Category:** Developer Tooling & Host Tools

## Inspiration

A green host test does not demonstrate a QNX build. A binary with the right architecture does not demonstrate that it ran. I wanted a small tool that makes those distinctions visible and helps developers collect useful evidence while learning QNX.

## What it does

The Python host tool checks for the QNX development environment, invokes QNX qcc for x86_64 or AArch64, checks the resulting ELF architecture, and records build output and source/binary hashes. A companion QNX-specific C probe measures wake-up lateness using absolute sleeps and QNX's nanosecond monotonic clock API. The host validates captured data and generates offline HTML and JSON reports with timing percentiles and configurable budget violations.

## How QNX is used

`probe/timing_probe.c` includes `sys/neutrino.h`, checks QNX target-header version, and calls `ClockPeriod()` and `clock_gettime_mon_ns()`. `inspector.py` uses QNX compiler variants and validates the QNX OS 8.0 capture format. The README documents the intended QNX OS 8.0 x86_64 QEMU target and SDP 8.0 toolchain.

## Current evidence

15 host tests passed on Linux. The local missing-SDK report is included. QNX cross-compilation and target execution remain unverified. Replace this paragraph with actual build and runtime results after completing the README workflow; do not infer successful target execution from host tests.

## Submission checklist

- [x] Create a new public repository and upload all project files, including the root MIT LICENSE.
- [ ] Run actual SDP 8.0 build and retain compiler report and binary hash.
- [ ] Capture a QNX OS 8.0 run and include capture, report, and environment notes.
- [ ] Record and publish a YouTube demonstration under three minutes; use original narration and no music or third-party logos/assets without permission.
- [ ] Fill in public repository URL and public YouTube URL.
- [ ] Select Developer Tooling & Host Tools.
- [ ] Optionally publish `docs/CODELAB.md` and supply its public URL for the tutorial bonus.
- [ ] Review the current official rules and submit before the deadline.

Repository URL: https://github.com/CreigT/qnx-evidence-inspector. YouTube URL: pending. Codelab URL: pending.
