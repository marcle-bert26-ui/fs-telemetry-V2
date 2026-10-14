# FS Telemetry

Télémétrie pour voiture Formula Student : lecture CAN d'une **MaxxECU Sport**, transmission radio **868 MHz (LoRa)** jusqu'au stand, avec un dashboard PC Python en première étape puis Unity.

```
MaxxECU ──CAN 500k──► [MCP2515] ► [Arduino Nano] ──SPI──► [LoRa 868] ~~~► [LoRa 868] ► [Nano base] ──USB──► PC / Python puis Unity
                      └──────────── voiture ────────────┘                └────────── stand ──────────┘
```

## Structure

| Section | Fichiers | Rôle |
|---|---|---|
| Firmware commun | `firmware/common/` | Définition de la trame partagée voiture/base |
| Firmware voiture | `firmware/car/` | CAN → trame → radio (PlatformIO, Nano) |
| Firmware base | `firmware/base/` | Radio → USB série (PlatformIO, Nano) |
| PC — Python | `pc/python/` | Application desktop et outils Python |
| PC — Python / interface | `pc/python/ui/` | Fenêtre et composants graphiques PyQt5/pyqtgraph |
| PC — Python / télémétrie | `pc/python/telemetry/` | Protocole binaire et enregistrement/relecture CSV |
| PC — Python / outils | `pc/python/tools/` | Simulateur et journaliseur série |
| PC — Python / identité visuelle | `pc/python/assets/` | Logo EIGSI Formula Student et licence de l’image |
| PC — Unity | `pc/unity/` | Dashboard Unity prévu dans une prochaine étape |
| Tests | `tests/dashboard/`, `tests/protocol/` | Tests organisés par composant |
| Documentation | `docs/` | Architecture, hardware, protocole et plans |
| Hardware et scripts | `hardware/`, `scripts/` | Schémas, BOM et automatisation GitHub |

## Démarrage rapide

```bash
git clone <url> && cd fs-telemetry
pip install platformio -r requirements-dev.txt
pio run -d firmware/car      # compile le firmware voiture
pio run -d firmware/base     # compile le firmware base
python -m pc.python.tools.fake_base --tcp 5555   # lance le simulateur (terminal 1)
python -m pc.python.app                         # lance le dashboard PC Python (terminal 2)
python -m pytest tests
```

Le dashboard se connecte au port série de la base ou à un serveur TCP, affiche les mesures disponibles dans la trame, enregistre les sessions en CSV et permet de les relire. Pour installer uniquement le nécessaire à l’application (sans pytest ni PlatformIO), utilise `pip install -r requirements.txt`.

Par défaut, les sessions CSV sont proposées dans `Documents/EIGSI Formula Student/Telemetry` (Windows : `Documents\EIGSI Formula Student\Telemetry`). Le bouton d’enregistrement permet de choisir un autre emplacement; « Ouvrir le dossier » ouvre le dossier par défaut.

Les tests sont séparés par composant : `tests/protocol/` couvre les trames et le CRC; `tests/dashboard/` couvre l’interface PC et les sessions CSV.

Initialiser GitHub (labels, milestones, backlog) : voir `scripts/setup_github.sh`.

## Documentation
- [Plan projet](docs/project-plan.md) · [Backlog](docs/backlog.md) · [Architecture](docs/architecture.md)
- [Hardware](docs/hardware.md) · [Protocole](docs/protocol.md) · [Plan de tests](docs/test-plan.md)
- [Contribuer](CONTRIBUTING.md)
