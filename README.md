# FS Telemetry

Télémétrie pour voiture Formula Student : lecture CAN d'une **MaxxECU Sport**, transmission radio **868 MHz (LoRa)** jusqu'au stand, affichage sur PC avec **Unity (licence Personal, gratuite)**.

```
MaxxECU ──CAN 500k──► [MCP2515] ► [Arduino Nano] ──SPI──► [LoRa 868] ~~~► [LoRa 868] ► [Nano base] ──USB──► PC / Unity
                      └──────────── voiture ────────────┘                └────────── stand ──────────┘
```

## Structure

| Dossier | Contenu |
|---|---|
| `firmware/common/` | Définition de la trame (partagée voiture / base) |
| `firmware/car/` | Firmware voiture (PlatformIO, Nano) : CAN → trame → radio |
| `firmware/base/` | Firmware stand : radio → USB série |
| `pc/tools/` | Simulateur de trames et utilitaires Python |
| `pc/unity/` | Projet Unity (dashboard) |
| `docs/` | Architecture, hardware, protocole, plan projet, tests |
| `hardware/` | Schémas, BOM, photos de câblage |
| `scripts/` | Automatisation GitHub (labels, milestones, issues) |

## Démarrage rapide

```bash
git clone <url> && cd fs-telemetry
pip install platformio pyserial
pio run -d firmware/car      # compile le firmware voiture
pio run -d firmware/base     # compile le firmware base
python pc/tools/fake_base.py --tcp 5555   # simule la base (sans hardware)
python -m unittest discover tests
```

Initialiser GitHub (labels, milestones, backlog) : voir `scripts/setup_github.sh`.

## Documentation
- [Plan projet](docs/project-plan.md) · [Backlog](docs/backlog.md) · [Architecture](docs/architecture.md)
- [Hardware](docs/hardware.md) · [Protocole](docs/protocol.md) · [Plan de tests](docs/test-plan.md)
- [Contribuer](CONTRIBUTING.md)
