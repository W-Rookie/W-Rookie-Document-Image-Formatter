# Changelog

## 1.4.1 - 2026-11-17

- Keeps the status bar and Start button permanently visible at every supported window size
- Adds a scrollable options panel so every setting remains reachable on smaller displays
- Rebuilds the unified Windows, macOS, Linux and source packages from the same codebase

## 1.4.0 - 2026-11-17

- Replaces the misunderstood alignment-axis controls with physical photo sizing
- Adds width and height input in millimetres or centimetres with optional aspect locking
- Supports exact sizing or proportional fit-to-box sizing for DrawingML, legacy VML and HWP pictures
- Adds an original black/crimson eclipse background and platform-aware Korean GUI fonts
- Adds physical-size, validation, asset-packaging and GUI regression coverage

## 1.3.0 - 2026-11-17

- Adds independent horizontal-center and vertical-center controls to the GUI and engines
- Supports horizontal-only, vertical-only, both-axis and border-only processing
- Redesigns the desktop GUI with a premium black, charcoal and crimson visual system
- Adds axis-specific DOCX/HWP regression tests and dark-theme GUI checks

## 1.2.0 - 2026-11-17

- Renames the program, GUI, distribution, commands and release artifacts to W-Rookie
- Adds separate Windows, macOS and Linux setup/run packages
- Adds native three-OS build and GitHub Release automation
- Limits HWP/HWPX selection to Windows while keeping DOCX available on every OS
- Expands the README and bundled guides with complete per-OS setup and usage steps
- Fixes a Tkinter internal method-name collision that prevented the GUI from opening
- Shows the actual exception summary in the startup error dialog
- Adds a regression test for successful GUI class initialization

## 1.1.1 - 2026-11-17

- Detects both the Windows `py -3` launcher and the `python` command
- Keeps setup failures visible and writes `setup-error.log`
- Starts the GUI with `pythonw.exe`, without leaving a console window open
- Shows a GUI error dialog and writes `docpic-align-error.log` on startup crashes
- Adds regression tests for the Windows setup and GUI launchers

## 1.1.0 - 2026-11-17

- Reworked README as a complete Korean GUI user manual
- Unified normal launch commands on the desktop GUI
- Added mandatory preflight security scanning before document automation
- Blocks macros, HWP scripts, ActiveX, OLE, executable payloads, unsafe ZIP paths,
  XML entities, dangerous external links and ZIP-bomb patterns
- Added optional Windows Defender scanning without automatic remediation
- Added hardened XML parsing and OLE compound-file structure validation
- Added adversarial security fixtures; automated suite now contains 27 tests

## 1.0.0 - 2026-11-17

- DOCX/HWP/HWPX batch processing
- Smart alignment and absolute page-center modes
- Configurable solid picture border, defaulting to black 1 pt
- Streaming DOCX package copy for large embedded media
- Korean desktop UI, CLI, diagnostics, cancellation and atomic output
- Automated OOXML tests and an opt-in large-file stress test
