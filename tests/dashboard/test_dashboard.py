import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication, QLabel

from pc.python.telemetry.protocol import decode, encode
from pc.python.ui.dashboard import LOGO_PATH, TelemetryWindow


class TestDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = TelemetryWindow()

    def tearDown(self):
        self.window.close()

    def test_displays_decoded_values_and_status(self):
        frame = decode(encode(1, 1000, 8000, 500, 1000, 1000, 1380, 900, 350, 700, flags=2))

        self.window._display_frame(frame)

        self.assertEqual(self.window.metrics["RPM"].value.text(), "8000 tr/min")
        self.assertEqual(self.window.metrics["TPS"].value.text(), "50.0 %")
        self.assertEqual(self.window.metrics["Lambda"].value.text(), "1.000")
        self.assertEqual(self.window.metrics["Batterie"].value.text(), "13.80 V")
        self.assertEqual(self.window.flags_label.text(), "ECU active")
        self.assertEqual(self.window.frame_count_label.text(), "Trames : 1")

    def test_displays_missing_measurements(self):
        frame = decode(encode(1, 1000, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
                              -0x8000, -0x8000, -0x8000, flags=0))

        self.window._display_frame(frame)

        for metric in ("RPM", "TPS", "MAP", "Lambda", "Batterie", "CLT", "IAT", "EGT"):
            with self.subTest(metric=metric):
                self.assertEqual(self.window.metrics[metric].value.text(), "N/D")

    def test_loads_application_icon_and_brand_logo(self):
        self.assertFalse(self.window.windowIcon().isNull())
        self.assertTrue(LOGO_PATH.is_file())
        logo = self.window.findChild(QLabel, "brandLogo")
        self.assertIsNotNone(logo)
        self.assertFalse(logo.pixmap().isNull())

    def test_default_recording_folder_is_under_documents(self):
        self.assertEqual(
            self.window.recordings_directory.parts[-2:],
            ("EIGSI Formula Student", "Telemetry"),
        )


if __name__ == "__main__":
    unittest.main()
