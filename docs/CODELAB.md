# Codelab: distinguish host success from QNX target evidence

**Outcome:** build a QNX-specific probe, collect 1,000 timing samples, and interpret an offline report.

**Prerequisites:** Python 3.10+, QNX SDP 8.0 on a supported host, and a running QNX OS 8.0 x86_64 QEMU image. Installation time depends on download and account access; reserve 30–60 minutes after prerequisites are available. SDK and image distribution is handled by QNX; this project includes neither.

1. Download the repository. Run the README host test command. Notice that it requires no QNX SDK. This proves the host code's tested behavior only.
2. Run `doctor` before loading your SDK environment. If prerequisites are absent, examine the diagnostic and exit code 2.
3. Load your installed SDP 8.0 environment and run the README build command. Read `build/x86_64/report.json`. Identify compiler arguments, source hash, binary hash, and the separate runtime status.
4. On the QNX target, run `uname -a`, transfer the probe, and run it as described in README. Preserve `capture.csv` and target configuration notes.
5. Analyze the capture. Locate median, p99 and maximum. Lateness equals actual wake time minus scheduled wake time; it does not measure application computation time.
6. Choose a different budget and rerun analysis in a separate report directory. Explain why changing a budget changes pass/fail counts but does not change measurements.
7. Make a copy of the capture and remove its final sample line. Analyze the copy. It should fail validation rather than silently report misleading statistics. Keep the original intact.
8. Compare idle and loaded target captures if desired, documenting the workload and environment. Do not conclude that either experiment establishes a worst-case guarantee.

**Check your understanding:** Why is a Linux ELF with the correct CPU architecture insufficient proof of QNX compatibility? Why must host test results and imported runtime captures be labeled separately? Why can a QEMU timing result change when the host is busy?

**Troubleshooting:** Missing qcc: source the real SDK environment. Header version error: use SDP 8.0, not a host compiler or a different SDK. Wrong ELF architecture: select the matching target. Invalid release: inspect target uname output; do not edit the capture to bypass validation. Truncated capture: check target exit status and repeat the transfer. Budget failure: inspect the measured distribution before changing the budget.
