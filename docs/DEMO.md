# Demo recording plan — 2 minutes 40 seconds

Record real execution after installing QNX SDP 8.0 and booting a target. Do not splice synthetic test fixtures into target evidence. Use your own narration; no music is needed.

- **0:00–0:20:** Explain the problem: host tests, QNX compilation, and target execution are different evidence. Show project name and category.
- **0:20–0:45:** Run `python3 inspector.py doctor`, then `build --target x86_64 --out build/x86_64`. Show the actual qcc command and build result.
- **0:45–1:15:** Show the target terminal, `uname -a`, and `./timing-probe > capture.csv`. Let the real 10-second capture finish. Explain the QNX clock functions.
- **1:15–1:45:** Transfer the capture to the host and run `analyze capture.csv --out report`. Open the report. Explain p99 and maximum wake-up lateness in plain language.
- **1:45–2:10:** Rerun with a tighter timing budget. Explain that a budget violation produces exit code 3 and retains the report; do not promise a violation if your measurement does not show one.
- **2:10–2:30:** Show the host tests and relevant QNX source functions. Explain imported logs are not cryptographic attestation and QEMU results are not hardware guarantees.
- **2:30–2:40:** Show the public repository and build instructions.

If compilation takes longer, shorten narration or edit waiting time while clearly labeling the edit. Total video must remain below three minutes.
