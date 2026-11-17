from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from docpicalign.models import BorderStyle, JobOptions, OutputMode, fitted_dimensions
from docpicalign.paths import output_path_for


class ModelAndPathTests(unittest.TestCase):
    def test_border_normalizes_hex(self) -> None:
        border = BorderStyle(1, "#aabbcc")
        self.assertEqual(border.color, "AABBCC")

    def test_invalid_border_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BorderStyle(0, "000000")
        with self.assertRaises(ValueError):
            BorderStyle(1, "black")

    def test_physical_size_validation_rejects_unsafe_values(self) -> None:
        for value in (0, -1, 1000.1, float("inf"), float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                JobOptions(resize_width_mm=value)

    def test_aspect_lock_fits_inside_the_requested_box(self) -> None:
        width, height = fitted_dimensions(400, 200, 100, 100, True)
        self.assertEqual((width, height), (100, 50))

    def test_unlocked_size_uses_exact_dimensions(self) -> None:
        width, height = fitted_dimensions(400, 200, 100, 80, False)
        self.assertEqual((width, height), (100, 80))

    def test_copy_output_never_clobbers_existing_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "보고서.docx"
            source.touch()
            first = folder / "보고서_사진정렬.docx"
            first.touch()
            output = output_path_for(source, JobOptions())
            self.assertEqual(output.name, "보고서_사진정렬_2.docx")

    def test_overwrite_targets_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.docx"
            source.touch()
            options = JobOptions(output_mode=OutputMode.OVERWRITE)
            self.assertEqual(output_path_for(source, options), source.resolve())


if __name__ == "__main__":
    unittest.main()
