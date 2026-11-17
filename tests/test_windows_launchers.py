from __future__ import annotations

import unittest
from pathlib import Path

from docpicalign.app import WRookieApp

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class WindowsLauncherTests(unittest.TestCase):
    def test_setup_supports_both_python_commands_and_preserves_errors(self) -> None:
        setup = (PROJECT_ROOT / "setup.bat").read_text(encoding="utf-8")

        self.assertIn("where py", setup)
        self.assertIn("where python", setup)
        self.assertIn("sys.version_info >= (3, 10)", setup)
        self.assertIn("setup-error.log", setup)
        self.assertIn("pause", setup)

    def test_run_uses_no_console_python_launcher(self) -> None:
        launcher = (PROJECT_ROOT / "run.bat").read_text(encoding="utf-8")

        self.assertIn("pythonw.exe", launcher)
        self.assertIn("run_gui.pyw", launcher)
        self.assertIn("w-rookie-error.log", launcher)

    def test_gui_launcher_compiles(self) -> None:
        source = (PROJECT_ROOT / "run_gui.pyw").read_text(encoding="utf-8")

        compile(source, "run_gui.pyw", "exec")

    def test_gui_does_not_override_tkinter_internal_options_method(self) -> None:
        self.assertNotIn("_options", WRookieApp.__dict__)
        self.assertIn("_build_job_options", WRookieApp.__dict__)

    def test_w_rookie_branding_is_used_by_distribution_and_launchers(self) -> None:
        pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        app = (PROJECT_ROOT / "src" / "docpicalign" / "app.py").read_text(encoding="utf-8")
        setup = (PROJECT_ROOT / "setup.bat").read_text(encoding="utf-8")
        launcher = (PROJECT_ROOT / "run.bat").read_text(encoding="utf-8")

        self.assertIn('name = "w-rookie"', pyproject)
        self.assertIn('self.title("W-Rookie', app)
        self.assertIn("W-Rookie Setup", setup)
        self.assertIn("W-Rookie Launcher", launcher)

    def test_gui_exposes_physical_size_controls_and_dark_red_theme(self) -> None:
        app = (PROJECT_ROOT / "src" / "docpicalign" / "app.py").read_text(encoding="utf-8")
        background = PROJECT_ROOT / "src" / "docpicalign" / "assets" / "background.png"
        pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("02  사진 크기", app)
        self.assertIn("크기 조절 사용", app)
        self.assertIn('("mm", "cm")', app)
        self.assertIn("원본 비율 유지", app)
        self.assertIn('BG = "#08090C"', app)
        self.assertIn('ACCENT = "#E50914"', app)
        self.assertTrue(background.is_file())
        self.assertGreater(background.stat().st_size, 100_000)
        self.assertIn('docpicalign = ["assets/*.png"]', pyproject)

    def test_macos_and_linux_launchers_validate_runtime(self) -> None:
        setup = (PROJECT_ROOT / "setup.sh").read_text(encoding="utf-8")
        launcher = (PROJECT_ROOT / "run.sh").read_text(encoding="utf-8")

        self.assertIn("python3 python", setup)
        self.assertIn("import tkinter", setup)
        self.assertIn("Python 3.10 or newer", setup)
        self.assertIn("exec .venv/bin/python -m docpicalign", launcher)

    def test_release_workflow_builds_all_three_operating_systems(self) -> None:
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("windows-latest", workflow)
        self.assertIn("macos-latest", workflow)
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("PyInstaller", workflow)
        self.assertIn("--collect-data docpicalign", workflow)

    def test_start_button_is_fixed_below_the_scrollable_options(self) -> None:
        app = (PROJECT_ROOT / "src" / "docpicalign" / "app.py").read_text(encoding="utf-8")

        self.assertIn('body.grid(row=2, column=0, sticky="nsew", padx=30)', app)
        self.assertIn('bottom.grid(row=3, column=0, sticky="ew"', app)
        self.assertIn("command=self._start", app)
        self.assertIn("yscrollcommand=right_scrollbar.set", app)


if __name__ == "__main__":
    unittest.main()
