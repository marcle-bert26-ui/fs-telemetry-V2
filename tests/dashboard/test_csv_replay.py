import os
import tempfile
import unittest

from pc.python.telemetry.csv_replay import CsvRecorder, load_csv
from pc.python.telemetry.protocol import FIELDS


class TestCsvReplay(unittest.TestCase):
    def setUp(self):
        self.frame = dict(zip(FIELDS, range(len(FIELDS))))

    def test_record_and_reload_frame(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as file:
            path = file.name
        try:
            recorder = CsvRecorder(path)
            recorder.write(self.frame)
            recorder.close()
            self.assertEqual(load_csv(path), [self.frame])
        finally:
            os.unlink(path)

    def test_rejects_missing_columns(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as file:
            file.write("seq,t_ms\n1,100\n")
            path = file.name
        try:
            with self.assertRaisesRegex(ValueError, "Colonnes manquantes"):
                load_csv(path)
        finally:
            os.unlink(path)

    def test_reports_invalid_row(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", newline="", delete=False) as file:
            file.write(",".join(FIELDS) + "\n")
            file.write(",".join(["not-an-integer"] + ["0"] * (len(FIELDS) - 1)) + "\n")
            path = file.name
        try:
            with self.assertRaisesRegex(ValueError, "ligne 2"):
                load_csv(path)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
