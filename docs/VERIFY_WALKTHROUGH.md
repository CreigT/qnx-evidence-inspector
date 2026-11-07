# VERIFY Walkthrough — Host Checks and Report Boundaries

**Goal:** Confirm host tests pass and that reports do not claim unverified QNX runtime success.

## Steps
1. From the repo root run: `python3 -m unittest discover -s tests -v`
2. Run `python3 inspector.py doctor` and note the exit code and any missing SDK messages.
3. If a prior build artifact exists, run `python3 inspector.py inspect <binary> --target x86_64` and confirm architecture evidence is recorded without setting runtime_verified true solely from the host check.
4. Feed a deliberately truncated or invalid capture.csv to `python3 inspector.py analyze` and confirm it rejects or flags the input while still writing a report.
5. Confirm no command in the workflow executes a QNX binary on the Linux host.

## Pass Criteria
- Host tests pass.
- Reports distinguish build/architecture evidence from runtime verification.
- Invalid captures are handled without silent success.
- No host execution of the target binary.

## Fail Criteria
- Host tests fail.
- Report claims runtime verification when only host checks ran.
- Invalid capture is accepted as valid without flags.

This verifies the host tooling boundary. QNX target verification requires the SDK and a real run.
