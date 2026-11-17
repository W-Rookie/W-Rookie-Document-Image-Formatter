from __future__ import annotations

import unittest

from docpicalign.models import AlignMode, BorderStyle, JobOptions
from docpicalign.processors.hwp import HwpProcessor


class FakeSet:
    def __init__(self) -> None:
        self.values = {}
        self.children = {}

    def SetItem(self, name, value) -> None:
        self.values[name] = value

    def CreateItemSet(self, name, _kind):
        child = FakeSet()
        self.children[name] = child
        return child


class FakeShape:
    def __init__(self) -> None:
        self.HSet = FakeSet()


class FakeAction:
    def __init__(self) -> None:
        self.runs = []
        self.executions = []

    def Run(self, name):
        self.runs.append(name)
        return True

    def GetDefault(self, name, _hset):
        self.runs.append(f"default:{name}")

    def Execute(self, name, hset):
        self.executions.append((name, hset))
        return True


class FakeParameters:
    def __init__(self) -> None:
        self.HShapeObject = FakeShape()


class FakeCtrl:
    def __init__(self, ctrl_id="gso", description="그림", next_ctrl=None) -> None:
        self.CtrlID = ctrl_id
        self.UserDesc = description
        self.Next = next_ctrl

    def GetAnchorPos(self, _index):
        return "anchor"


class FakeHwp:
    def __init__(self) -> None:
        self.HAction = FakeAction()
        self.HParameterSet = FakeParameters()
        self.positions = []

    def SetPosBySet(self, value):
        self.positions.append(value)

    def FindCtrl(self):
        return True

    def RGBColor(self, red, green, blue):
        return red | (green << 8) | (blue << 16)

    def HwpLineType(self, _label):
        return 1

    def HwpLineWidth(self, _label):
        return 6


class HwpProcessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = HwpProcessor()

    def test_one_point_uses_nearest_hancom_width(self) -> None:
        self.assertEqual(self.processor._nearest_hwp_width(1.0), 0.4)

    def test_only_picture_controls_are_selected(self) -> None:
        tail = FakeCtrl("tbl", "표")
        shape = FakeCtrl("gso", "사각형", tail)
        picture = FakeCtrl("gso", "그림", shape)
        fake = FakeHwp()
        fake.HeadCtrl = picture
        self.assertEqual(self.processor._picture_controls(fake), [picture])

    def test_page_mode_sets_center_position_and_border(self) -> None:
        fake = FakeHwp()
        options = JobOptions(
            align_mode=AlignMode.PAGE,
            border=BorderStyle(1.0, "112233"),
        )
        self.processor._format_picture(fake, FakeCtrl(), options, 0.4)
        shape = fake.HParameterSet.HShapeObject.HSet
        self.assertEqual(shape.values["TreatAsChar"], 0)
        self.assertEqual(shape.values["HorzRelTo"], 1)
        self.assertEqual(shape.values["VertRelTo"], 1)
        self.assertEqual(shape.values["HorzAlign"], 1)
        self.assertEqual(shape.values["VertAlign"], 1)
        line = shape.children["ShapeDrawLineAttr"]
        self.assertEqual(line.values["Style"], 1)
        self.assertEqual(line.values["Width"], 6)
        self.assertEqual(line.values["Color"], 0x332211)
        self.assertIn("ParagraphShapeAlignCenter", fake.HAction.runs)

    def test_smart_mode_requests_table_vertical_center_without_floating(self) -> None:
        fake = FakeHwp()
        self.processor._format_picture(fake, FakeCtrl(), JobOptions(), 0.4)
        shape = fake.HParameterSet.HShapeObject.HSet
        self.assertNotIn("TreatAsChar", shape.values)
        self.assertIn("TableVAlignCenter", fake.HAction.runs)

    def test_exact_picture_size_without_aspect_lock(self) -> None:
        fake = FakeHwp()
        options = JobOptions(
            resize_width_mm=25.4,
            resize_height_mm=12.7,
            lock_aspect_ratio=False,
        )
        self.processor._format_picture(fake, FakeCtrl(), options, 0.4)
        shape = fake.HParameterSet.HShapeObject.HSet
        self.assertEqual(shape.values["KeepAspectRatio"], 0)
        self.assertEqual(shape.values["Width"], 7200)
        self.assertEqual(shape.values["Height"], 3600)

    def test_aspect_locked_picture_size_fits_original_ratio(self) -> None:
        fake = FakeHwp()
        shape = fake.HParameterSet.HShapeObject.HSet
        shape.values.update({"Width": 7200, "Height": 3600})
        options = JobOptions(
            resize_width_mm=50.8,
            resize_height_mm=25.4,
            lock_aspect_ratio=True,
        )
        self.processor._format_picture(fake, FakeCtrl(), options, 0.4)
        self.assertEqual(shape.values["KeepAspectRatio"], 1)
        self.assertEqual(shape.values["Width"], 14400)
        self.assertEqual(shape.values["Height"], 7200)


if __name__ == "__main__":
    unittest.main()
