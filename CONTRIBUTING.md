# Contributing

1. Create a branch from `main`.
2. Run `python -m unittest discover -s tests -v`.
3. Run `python -m ruff check run_gui.pyw src tests scripts`.
4. Run `python -m ruff format --check src tests scripts`.
5. Keep test documents synthetic or anonymized; never commit private documents.
6. For HWP changes, record the Hancom Office version and test both `.hwp` and `.hwpx`.

Bug reports should include the OS, Python version, Hancom version when relevant,
alignment mode, and a minimal document that contains no sensitive information.
