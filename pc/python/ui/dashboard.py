"""PC telemetry dashboard UI.

Launch with ``python -m pc.python.app`` after installing ``requirements.txt``.
"""

import math
import socket
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import pyqtgraph as pg
import serial
from PyQt5.QtCore import QStandardPaths, QThread, QTimer, QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pc.python.telemetry.csv_replay import CsvRecorder, load_csv
from pc.python.telemetry.protocol import extract_frames

ASSETS_DIR = Path(__file__).parents[1] / "assets"
LOGO_PATH = ASSETS_DIR / "eigsi_formula_student.png"
MAX_SAMPLES = 600
STALE_AFTER_SECONDS = 1.0
FLAG_CAN_TIMEOUT = 1 << 0
FLAG_ECU_ALIVE = 1 << 1
FLAG_LOW_BATTERY = 1 << 2


def application_icon() -> QIcon:
    logo = QPixmap(str(LOGO_PATH))
    if logo.isNull():
        raise FileNotFoundError(f"Logo EIGSI Formula Student introuvable : {LOGO_PATH}")

    pixmap = QPixmap(128, 128)
    pixmap.fill(QColor("#10151c"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    scaled_logo = logo.scaled(112, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    painter.drawPixmap(
        (pixmap.width() - scaled_logo.width()) // 2,
        (pixmap.height() - scaled_logo.height()) // 2,
        scaled_logo,
    )
    painter.end()
    return QIcon(pixmap)


class LiveReader(QThread):
    frame_received = pyqtSignal(object)
    connected = pyqtSignal()
    read_error = pyqtSignal(str)

    def __init__(self, source: str, address: str, baud: int, parent: QWidget | None = None):
        super().__init__(parent)
        self.source = source
        self.address = address
        self.baud = baud

    def run(self) -> None:
        buffer = bytearray()
        try:
            if self.source == "Série":
                stream: Any = serial.Serial(self.address, self.baud, timeout=0.2)
            else:
                host, port_text = self.address.rsplit(":", 1)
                stream = socket.create_connection((host, int(port_text)), timeout=5)
                stream.settimeout(0.2)

            with stream:
                self.connected.emit()
                while not self.isInterruptionRequested():
                    try:
                        chunk = stream.read(256) if self.source == "Série" else stream.recv(256)
                    except socket.timeout:
                        continue
                    if self.source == "TCP" and not chunk:
                        raise ConnectionError("Le serveur TCP a fermé la connexion.")
                    buffer.extend(chunk)
                    for frame in extract_frames(buffer):
                        self.frame_received.emit(frame)
        except (OSError, ValueError, serial.SerialException) as error:
            if not self.isInterruptionRequested():
                self.read_error.emit(str(error))


class MetricCard(QGroupBox):
    def __init__(self, title: str):
        super().__init__(title)
        self.value = QLabel("—")
        self.value.setObjectName("metricValue")
        layout = QVBoxLayout(self)
        layout.addWidget(self.value)


class TelemetryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EIGSI Formula Student — Telemetry")
        self.setWindowIcon(application_icon())
        self.resize(1280, 850)
        documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        self.recordings_directory = (
            Path(documents_path) if documents_path else Path.home() / "Documents"
        ) / "EIGSI Formula Student" / "Telemetry"
        self.reader: LiveReader | None = None
        self.recorder: CsvRecorder | None = None
        self.last_frame_at: float | None = None
        self.previous_sequence: int | None = None
        self.lost_frames = 0
        self.received_frames = 0
        self.first_frame_ms: int | None = None
        self.last_replay_ms: int | None = None
        self.replay_frames: list[dict[str, int]] = []
        self.replay_index = 0
        self.replaying = False
        self.elapsed: deque[float] = deque(maxlen=MAX_SAMPLES)
        self.series: dict[str, deque[float]] = {
            key: deque(maxlen=MAX_SAMPLES)
            for key in ("rpm", "tps", "map", "clt", "iat", "egt")
        }

        self._build_ui()
        self.replay_timer = QTimer(self)
        self.replay_timer.setSingleShot(True)
        self.replay_timer.timeout.connect(self._show_next_replay_frame)
        self.stale_timer = QTimer(self)
        self.stale_timer.timeout.connect(self._update_stale_status)
        self.stale_timer.start(250)

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_connection_panel())
        layout.addWidget(self._build_metrics())
        layout.addWidget(self._build_charts(), stretch=1)
        layout.addWidget(self._build_status_panel())
        self.setCentralWidget(root)

        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #10151c; color: #e5edf5; }
            QGroupBox { border: 1px solid #34404d; border-radius: 6px; margin-top: 8px; padding: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QLabel#metricValue { color: #54d6c8; font-size: 22px; font-weight: bold; }
            QPushButton { padding: 6px 12px; }
            QLineEdit, QComboBox { padding: 5px; }
            """
        )

    def _build_header(self) -> QWidget:
        header = QWidget()
        row = QHBoxLayout(header)
        row.setContentsMargins(14, 8, 14, 8)
        logo = QLabel()
        pixmap = QPixmap(str(LOGO_PATH))
        if pixmap.isNull():
            raise FileNotFoundError(f"Logo EIGSI Formula Student introuvable : {LOGO_PATH}")
        logo.setPixmap(pixmap.scaled(150, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setObjectName("brandLogo")
        logo.setAccessibleName("Logo EIGSI Formula Student")
        row.addWidget(logo)

        title = QLabel("EIGSI FORMULA STUDENT")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #54d6c8;")
        subtitle = QLabel("Système de télémétrie — acquisition et analyse en temps réel")
        subtitle.setStyleSheet("font-size: 12px; color: #aab8c7;")
        text = QVBoxLayout()
        text.addWidget(title)
        text.addWidget(subtitle)
        row.addLayout(text)
        row.addStretch(1)
        return header

    def _build_connection_panel(self) -> QGroupBox:
        panel = QGroupBox("Connexion")
        form = QFormLayout(panel)
        row = QHBoxLayout()
        self.source_type = QComboBox()
        self.source_type.addItems(["Série", "TCP"])
        self.source_type.currentTextChanged.connect(self._update_source_fields)
        row.addWidget(self.source_type)

        self.address = QLineEdit("COM7")
        self.address.setPlaceholderText("Port série, ex. COM7")
        row.addWidget(self.address, stretch=1)
        self.tcp_host = QLineEdit("127.0.0.1")
        self.tcp_host.setMaximumWidth(180)
        self.tcp_port = QLineEdit("5555")
        self.tcp_port.setMaximumWidth(90)
        row.addWidget(self.tcp_host)
        row.addWidget(self.tcp_port)
        self.connect_button = QPushButton("Connecter")
        self.connect_button.clicked.connect(self._toggle_connection)
        row.addWidget(self.connect_button)
        form.addRow("Source", row)

        controls = QHBoxLayout()
        self.record_button = QPushButton("Enregistrer CSV")
        self.record_button.clicked.connect(self._toggle_recording)
        self.record_button.setEnabled(False)
        controls.addWidget(self.record_button)
        self.open_csv_button = QPushButton("Ouvrir un CSV")
        self.open_csv_button.clicked.connect(self._open_csv)
        controls.addWidget(self.open_csv_button)
        self.play_button = QPushButton("Lire")
        self.play_button.clicked.connect(self._toggle_replay)
        self.play_button.setEnabled(False)
        controls.addWidget(self.play_button)
        self.stop_replay_button = QPushButton("Arrêter")
        self.stop_replay_button.clicked.connect(self._stop_replay)
        self.stop_replay_button.setEnabled(False)
        controls.addWidget(self.stop_replay_button)
        form.addRow("Session", controls)
        self.recording_path_label = QLabel(
            f"Dossier CSV par défaut : {self.recordings_directory}"
        )
        self.recording_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.addRow("Enregistrements", self.recording_path_label)
        self.open_recordings_folder_button = QPushButton("Ouvrir le dossier")
        self.open_recordings_folder_button.clicked.connect(self._open_recordings_folder)
        form.addRow("", self.open_recordings_folder_button)
        self._update_source_fields()
        return panel

    def _build_metrics(self) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        self.metrics = {
            name: MetricCard(name)
            for name in ("RPM", "TPS", "MAP", "Lambda", "Batterie", "CLT", "IAT", "EGT")
        }
        for index, card in enumerate(self.metrics.values()):
            grid.addWidget(card, index // 4, index % 4)
        return container

    def _build_charts(self) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        pg.setConfigOptions(antialias=True, background="#10151c", foreground="#d7e0ea")
        self.plots: dict[str, tuple[Any, Any]] = {}
        specifications = (
            ("rpm", "Régime", "tr/min", "#54d6c8"),
            ("tps", "Accélérateur", "%", "#ffc857"),
            ("map", "Pression admission", "kPa", "#8cb4ff"),
            ("temps", "Températures", "°C", "#f27f7d"),
        )
        for index, (key, title, unit, color) in enumerate(specifications):
            plot = pg.PlotWidget(title=title)
            plot.setLabel("left", unit)
            plot.setLabel("bottom", "Temps", units="s")
            plot.showGrid(x=True, y=True, alpha=0.25)
            plot.setMinimumHeight(190)
            if key == "temps":
                plot.addLegend()
                curves = (
                    plot.plot(pen=pg.mkPen("#f27f7d", width=2), name="CLT"),
                    plot.plot(pen=pg.mkPen("#8cb4ff", width=2), name="IAT"),
                    plot.plot(pen=pg.mkPen("#ffc857", width=2), name="EGT"),
                )
            else:
                curves = (plot.plot(pen=pg.mkPen(color, width=2)),)
            self.plots[key] = (plot, curves)
            grid.addWidget(plot, index // 2, index % 2)
        return container

    def _build_status_panel(self) -> QGroupBox:
        panel = QGroupBox("État")
        row = QHBoxLayout(panel)
        self.status_label = QLabel("Déconnecté")
        self.frame_count_label = QLabel("Trames : 0")
        self.loss_label = QLabel("Pertes : 0")
        self.flags_label = QLabel("ECU : —")
        row.addWidget(self.status_label, stretch=1)
        row.addWidget(self.frame_count_label)
        row.addWidget(self.loss_label)
        row.addWidget(self.flags_label)
        return panel

    def _update_source_fields(self) -> None:
        tcp_selected = self.source_type.currentText() == "TCP"
        self.address.setVisible(not tcp_selected)
        self.tcp_host.setVisible(tcp_selected)
        self.tcp_port.setVisible(tcp_selected)

    def _toggle_connection(self) -> None:
        if self.reader is not None:
            self._stop_reader()
            return
        if self.replaying or self.stop_replay_button.isEnabled():
            QMessageBox.information(self, "Relecture en cours", "Arrête la relecture avant de te connecter.")
            return

        source = self.source_type.currentText()
        if source == "TCP":
            host = self.tcp_host.text().strip()
            if not host:
                QMessageBox.warning(self, "Hôte manquant", "Saisis l’adresse du serveur TCP.")
                return
            try:
                port = int(self.tcp_port.text())
                if not 1 <= port <= 65535:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Port invalide", "Le port TCP doit être compris entre 1 et 65535.")
                return
            address = f"{host}:{port}"
        else:
            address = self.address.text().strip()
            if not address:
                QMessageBox.warning(self, "Port série manquant", "Saisis le nom du port série.")
                return

        self.reader = LiveReader(source, address, 115200, self)
        self.reader.frame_received.connect(self._display_frame)
        self.reader.connected.connect(self._on_connected)
        self.reader.read_error.connect(self._on_reader_error)
        self.reader.finished.connect(self._on_reader_finished)
        self.connect_button.setEnabled(False)
        self.open_csv_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.status_label.setText("Connexion en cours…")
        self.reader.start()

    def _stop_reader(self) -> None:
        if self.reader is not None:
            self.reader.requestInterruption()
            self.connect_button.setEnabled(False)
            self.status_label.setText("Déconnexion…")

    def _on_connected(self) -> None:
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Déconnecter")
        self.record_button.setEnabled(True)
        self.open_csv_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.status_label.setText("Connecté — en attente de trames")

    def _on_reader_error(self, message: str) -> None:
        self.status_label.setText("Erreur de connexion")
        QMessageBox.warning(self, "Erreur de télémétrie", message)

    def _on_reader_finished(self) -> None:
        self.reader = None
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Connecter")
        self.record_button.setEnabled(False)
        self.open_csv_button.setEnabled(True)
        self.play_button.setEnabled(bool(self.replay_frames))
        self._stop_recording()
        if self.status_label.text() != "Erreur de connexion":
            self.status_label.setText("Déconnecté")

    def _toggle_recording(self) -> None:
        if self.recorder is not None:
            self._stop_recording()
            return
        try:
            self.recordings_directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            QMessageBox.critical(self, "Dossier CSV inaccessible", str(error))
            return
        default_name = f"telemetry_{datetime.now():%Y%m%d_%H%M%S}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer les données",
            str(self.recordings_directory / default_name),
            "Fichiers CSV (*.csv)",
        )
        if not path:
            return
        try:
            self.recorder = CsvRecorder(path)
        except OSError as error:
            QMessageBox.critical(self, "Erreur CSV", str(error))
            return
        self.recording_path_label.setText(f"Enregistrement CSV : {path}")
        self.record_button.setText("Arrêter l’enregistrement")
        self.status_label.setText(f"Enregistrement : {Path(path).name}")

    def _open_recordings_folder(self) -> None:
        try:
            self.recordings_directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            QMessageBox.critical(self, "Dossier CSV inaccessible", str(error))
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.recordings_directory))):
            QMessageBox.warning(
                self, "Ouverture impossible", f"Le dossier est disponible ici : {self.recordings_directory}"
            )

    def _stop_recording(self) -> None:
        recorder = self.recorder
        if recorder is None:
            return
        self.recorder = None
        self.record_button.setText("Enregistrer CSV")
        try:
            recorder.close()
        except OSError as error:
            QMessageBox.critical(self, "Erreur CSV", f"Impossible de finaliser le fichier : {error}")

    def _open_csv(self) -> None:
        if self.reader is not None or self.replaying:
            QMessageBox.information(self, "Source active", "Arrête la source en cours avant d’ouvrir un CSV.")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Ouvrir une session", "", "Fichiers CSV (*.csv)")
        if not path:
            return
        try:
            self.replay_frames = load_csv(path)
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "CSV invalide", str(error))
            return
        self._clear_history()
        self.replay_index = 0
        self.last_replay_ms = None
        self.play_button.setEnabled(True)
        self.status_label.setText(f"Prêt à relire : {Path(path).name} ({len(self.replay_frames)} trames)")

    def _toggle_source_controls(self, enabled: bool) -> None:
        self.source_type.setEnabled(enabled)
        self.address.setEnabled(enabled)
        self.tcp_host.setEnabled(enabled)
        self.tcp_port.setEnabled(enabled)
        self.open_csv_button.setEnabled(enabled)

    def _toggle_replay(self) -> None:
        if self.reader is not None:
            QMessageBox.information(self, "Source active", "Déconnecte la source live avant de relire un CSV.")
            return
        if self.replaying:
            self.replay_timer.stop()
            self.replaying = False
            self.play_button.setText("Lire")
            self.status_label.setText("Relecture en pause")
            return
        if not self.replay_frames:
            return
        if self.replay_index >= len(self.replay_frames):
            self.replay_index = 0
            self.last_replay_ms = None
            self._clear_history()
        self.replaying = True
        self.play_button.setText("Pause")
        self.stop_replay_button.setEnabled(True)
        self._toggle_source_controls(False)
        self._show_next_replay_frame()

    def _stop_replay(self) -> None:
        self.replay_timer.stop()
        self.replaying = False
        self.replay_index = 0
        self.last_replay_ms = None
        self.stop_replay_button.setEnabled(False)
        self.play_button.setText("Lire")
        self._clear_history()
        self.status_label.setText("Relecture arrêtée")
        self._toggle_source_controls(True)

    def _show_next_replay_frame(self) -> None:
        if not self.replaying or self.replay_index >= len(self.replay_frames):
            self.replaying = False
            self.play_button.setText("Lire")
            self.stop_replay_button.setEnabled(False)
            self.status_label.setText("Relecture terminée")
            self._toggle_source_controls(True)
            return

        frame = self.replay_frames[self.replay_index]
        self.last_replay_ms = frame["t_ms"]
        self.replay_index += 1
        self._display_frame(frame, replay=True)
        if self.replay_index >= len(self.replay_frames):
            self.replaying = False
            self.play_button.setText("Lire")
            self.stop_replay_button.setEnabled(False)
            self.status_label.setText("Relecture terminée")
            self._toggle_source_controls(True)
        else:
            next_ms = self.replay_frames[self.replay_index]["t_ms"]
            delay = (next_ms - self.last_replay_ms) & 0xFFFFFFFF
            self.replay_timer.start(max(10, min(delay, 1000)))

    def _clear_history(self) -> None:
        self.elapsed.clear()
        for values in self.series.values():
            values.clear()
        self.first_frame_ms = None
        for _, curves in self.plots.values():
            for curve in curves:
                curve.clear()

    def _display_frame(self, frame: dict[str, int], replay: bool = False) -> None:
        self.last_frame_at = time.monotonic()
        self.received_frames += 1
        if self.previous_sequence is not None:
            gap = (frame["seq"] - self.previous_sequence) & 0xFF
            if 1 < gap < 128:
                self.lost_frames += gap - 1
        self.previous_sequence = frame["seq"]
        self.frame_count_label.setText(f"Trames : {self.received_frames}")
        self.loss_label.setText(f"Pertes estimées : {self.lost_frames}")

        timestamp = frame["t_ms"]
        if self.first_frame_ms is None:
            self.first_frame_ms = timestamp
        elapsed = ((timestamp - self.first_frame_ms) & 0xFFFFFFFF) / 1000.0
        self.elapsed.append(elapsed)

        values = {
            "rpm": frame["rpm"],
            "tps": self._scaled(frame["tps_d"], 10, " %"),
            "map": self._scaled(frame["map_dkpa"], 10, " kPa"),
            "clt": self._scaled(frame["clt_d"], 10, " °C"),
            "iat": self._scaled(frame["iat_d"], 10, " °C"),
            "egt": self._scaled(frame["egt"], 1, " °C"),
        }
        labels = (
            ("RPM", self._scaled(frame["rpm"], 1, " tr/min")),
            ("TPS", values["tps"]),
            ("MAP", values["map"]),
            ("Lambda", self._scaled(frame["lambda_m"], 1000, "")),
            ("Batterie", self._scaled(frame["vbat_c"], 100, " V")),
            ("CLT", values["clt"]),
            ("IAT", values["iat"]),
            ("EGT", values["egt"]),
        )
        for name, text in labels:
            self.metrics[name].value.setText(text)

        for key in ("rpm", "tps", "map", "clt", "iat", "egt"):
            numeric = frame[{"tps": "tps_d", "map": "map_dkpa", "clt": "clt_d", "iat": "iat_d"}.get(key, key)]
            divisor = {"tps": 10, "map": 10, "clt": 10, "iat": 10}.get(key, 1)
            value = math.nan if numeric in (0xFFFF, -0x8000) else numeric / divisor
            self.series[key].append(value)

        self.plots["rpm"][1][0].setData(list(self.elapsed), list(self.series["rpm"]))
        self.plots["tps"][1][0].setData(list(self.elapsed), list(self.series["tps"]))
        self.plots["map"][1][0].setData(list(self.elapsed), list(self.series["map"]))
        for curve, key in zip(self.plots["temps"][1], ("clt", "iat", "egt")):
            curve.setData(list(self.elapsed), list(self.series[key]))
        self.status_label.setText("Relecture" if replay else "Données en direct")
        self._update_flags(frame)
        if self.recorder is not None and not replay:
            try:
                self.recorder.write(frame)
            except OSError as error:
                QMessageBox.critical(self, "Erreur CSV", f"Impossible d’écrire la trame : {error}")
                self._stop_recording()

    @staticmethod
    def _scaled(value: int, divisor: int, unit: str) -> str:
        if value == 0xFFFF or value == -0x8000:
            return "N/D"
        decimals = {1: 0, 10: 1, 100: 2, 1000: 3}[divisor]
        return f"{value / divisor:.{decimals}f}{unit}"

    def _update_flags(self, frame: dict[str, int]) -> None:
        flags = frame["flags"]
        status = "ECU active" if flags & FLAG_ECU_ALIVE else "ECU inactive"
        if flags & FLAG_CAN_TIMEOUT:
            status += " · CAN timeout"
        if flags & FLAG_LOW_BATTERY:
            status += " · batterie faible"
        self.flags_label.setText(status)

    def _update_stale_status(self) -> None:
        if self.last_frame_at is not None and self.reader is not None:
            if time.monotonic() - self.last_frame_at > STALE_AFTER_SECONDS:
                self.status_label.setText("Données périmées — aucune trame depuis 1 s")

    def closeEvent(self, event: Any) -> None:
        self.replay_timer.stop()
        self._stop_recording()
        if self.reader is not None:
            self.reader.requestInterruption()
            self.reader.wait(6000)
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("EIGSI Formula Student")
    app.setApplicationName("FS Telemetry")
    app.setWindowIcon(application_icon())
    window = TelemetryWindow()
    window.show()
    return app.exec_()
