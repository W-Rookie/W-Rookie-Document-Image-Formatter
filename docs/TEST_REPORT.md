# Test report

Tested on 2026-11-17 before the 1.4.1 source release.

## Automated results

- `ruff check run_gui.pyw src tests scripts`: passed
- `ruff format --check run_gui.pyw src tests scripts`: passed
- `python -m unittest discover -s tests -v`: 45/45 passed
- Tk virtual-display black/crimson eclipse GUI construction and render: passed
- Fixed-footer visibility at 1180×780 and minimum 1020×700 window sizes: passed
- Start-button click through document completion: passed
- GUI-to-engine mm/cm and aspect-lock option binding: passed
- 128 MB stored-media DOCX stress test: passed
- Media SHA-256 before/after processing: identical
- Python bytecode compilation: passed
- Python wheel build and content inspection: passed
- Clean wheel install, CLI diagnostics and virtual-display GUI launch: passed
- Extracted Linux ZIP setup, GUI launch and synthetic DOCX processing: passed
- macOS/Linux shell syntax and executable-permission inspection: passed
- Synthetic DOCX processing and headless LibreOffice open/export: passed

The automated suite covers DrawingML and legacy VML pictures, exact and
aspect-locked physical sizing, millimetre conversion, unsafe size validation,
exact DOCX 1 pt borders, document-flow and page-center positioning,
table-cell vertical alignment,
namespace compatibility, idempotency, cancellation, malformed input, output
collision handling, mocked Hancom parameter application, macros, HWP script
indicators, ActiveX, OLE, executable payloads, unsafe ZIP paths, XML entities,
dangerous external links, security-gate enforcement, and Windows launcher
regressions, and the Tkinter internal method-name collision that blocked GUI startup.

## Native integration still required

The source build environment is Linux. The Linux package and GUI were exercised,
but a live Hancom Office COM test, visual Windows GUI test, and physical macOS
test cannot be claimed here. Before publishing a release:

1. Run `test.bat` on Windows.
2. Run `run.bat`, then use **환경 진단**.
3. Process synthetic samples created with `scripts\create_sample.py`.
4. Open `.hwp`, `.hwpx`, and `.docx` results in the target office applications.
5. Build with `build.bat` and smoke-test `dist\W-Rookie\W-Rookie.exe` on a
   second Windows PC if possible.
6. Run `setup.command` and `run.command` on both Intel and Apple Silicon macOS
   when those machines are available.

Record the Windows, Microsoft Word, and Hancom Office versions in the GitHub
release notes.
