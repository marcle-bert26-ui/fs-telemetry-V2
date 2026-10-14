"""CSV recording and replay helpers for decoded telemetry frames."""

import csv
from pathlib import Path
from typing import TextIO

from pc.python.telemetry.protocol import FIELDS


class CsvRecorder:
    def __init__(self, path: str | Path):
        self._file: TextIO = open(path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=FIELDS)
        self._writer.writeheader()

    def write(self, frame: dict[str, int]) -> None:
        self._writer.writerow(frame)
        self._file.flush()

    def close(self) -> None:
        self._file.close()


def load_csv(path: str | Path) -> list[dict[str, int]]:
    frames: list[dict[str, int]] = []
    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("Le fichier CSV est vide.")

        missing = set(FIELDS) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Colonnes manquantes dans le CSV : {', '.join(sorted(missing))}.")

        try:
            for line_number, row in enumerate(reader, start=2):
                if not row or all(value is None or not value.strip() for value in row.values()):
                    continue
                try:
                    frames.append({field: int(row[field]) for field in FIELDS})
                except (TypeError, ValueError) as error:
                    raise ValueError(f"Valeur invalide à la ligne {line_number} du CSV.") from error
        except csv.Error as error:
            raise ValueError(f"CSV illisible : {error}") from error

    if not frames:
        raise ValueError("Le fichier CSV ne contient aucune trame.")
    return frames
