# QNX Build & Evidence Inspector Operational Card
**Host tool for QNX OS 8.0 timing probe build checks, architecture validation, and capture analysis**  
Sponsored by CREIGNIFICENT LLC · Status: Host tooling verified; QNX target execution not verified

## Purpose
Prevent common developer mistakes: compiling for the wrong architecture, analyzing truncated or invalid timing logs, or treating host tests as proof of a successful QNX run. Produce evidence-backed reports of what was checked.

## Trust Boundaries
- Host tests (15 passed on Linux, 2026-11-07) do not prove QNX compilation or target execution.
- QNX SDK is required for cross-build; this repo does not redistribute QNX binaries or licenses.
- Captures are operator-supplied and can be forged. Schema checks and hashes are not remote attestation.
- ELF architecture check confirms binary architecture but does not prove QNX origin.
- Tool does not execute the QNX binary on the host. No shell is used to invoke the compiler.
- Reports are diagnostic, not safety certification or worst-case execution-time analysis.

## Current Enforcement / Verified Status
- Python CLI, C probe source, ELF architecture validation, strict capture parser, JSON/HTML reports, and host tests are implemented.
- 15 host tests passed on Linux. QNX compilation and target execution have NOT been verified (SDK unavailable in development workspace).
- Input captures capped at 8 MiB / 100,000 samples. Generated HTML escapes input.

## Explicit Non-Goals
- Does not certify applications as QNX-compatible.
- Does not provide remote attestation or prove capture authenticity beyond schema/hash.
- Does not replace QNX SDK or target testing.
- Not a safety system or schedulability proof.

## Verification Points
1. Host unit tests pass (`python3 -m unittest discover -s tests -v`).
2. Doctor and inspect commands report architecture and build evidence without claiming runtime verification.
3. Analyze rejects invalid or truncated captures and still writes a report.
4. No QNX binary is executed on the host.

## Next Secure Step
Obtain QNX SDP 8.0, perform actual cross-build and target capture, and record the evidence in `evidence/` so `runtime_verified` can be set only when proven.
