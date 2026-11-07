# Validation record — November 7, 2026

Command: `python3 -m unittest discover -s tests -v`
Result: 15 tests passed on Linux.

Tests use synthetic input generated in temporary directories to exercise parser behavior. They are not QNX runtime evidence. Coverage includes statistics, budget exit code, invalid version/OS, timestamp ordering, truncation, ELF architecture mismatch, HTML escaping, absent SDK, compiler failure, and missing binary despite a successful compiler return code.

Command: `python3 inspector.py build --out evidence/local-sdk-check`
Result: exit 2, SDK missing; build_verified=false, runtime_verified=false.

Not performed: actual qcc compilation, QNX runtime capture, Windows/macOS execution, public CI run, public repository publication, or video upload.
