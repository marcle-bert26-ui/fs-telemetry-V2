# Backlog

Source de vérité : `scripts/backlog.tsv` (importé par `scripts/setup_github.sh`).


## M0 Setup

| # | Tâche | Label | Détail |
|---|---|---|---|
| 1 | Protéger la branche main | `area:infra` | Activer branch protection : PR + 1 review + CI requise. |
| 2 | Commander le matériel | `area:infra` | Nano x2, MCP2515 (vérifier quartz), RFM95 868 MHz x2, antennes, level-shifters, buck 12V-5V, fusibles, TVS, connecteurs. |
| 3 | Valider le règlement FS et la réglementation radio 868 MHz | `area:docs` | Puissance max, duty cycle, règles télémétrie/LV de l'année. |

## M1 CAN banc

| # | Tâche | Label | Détail |
|---|---|---|---|
| 4 | Identifier les CAN ID MaxxECU | `area:car` | Relever IDs/offsets/échelles dans la doc MaxxECU Default 1.2/1.3 et confirmer par sniffing. Compléter can_map.h et docs/protocol.md. |
| 5 | Câbler et tester le MCP2515 sur banc | `area:hardware` | Vérifier quartz, CAN_MCP_CLOCK, réception en listen-only, sans perturber l'ECU. |
| 6 | Décoder RPM, TPS, MAP, lambda | `area:car` | Implémenter can_decode, comparer avec MTune (test T4). |
| 7 | Décoder températures, vbat, EGT | `area:car` | Idem, gérer valeurs absentes (INVALID_*). |

## M2 Trame + radio

| # | Tâche | Label | Détail |
|---|---|---|---|
| 8 | Gérer FLAG_CAN_TIMEOUT et ECU alive | `area:car` | Test T8. |
| 9 | Level-shifter sur le SPI du module LoRa | `area:hardware` | Voir docs/hardware.md. Contrôle multimètre avant mise sous tension. |
| 10 | Émission LoRa 10 Hz non bloquante | `area:car` | Test T5, mesurer le temps d'émission réel. |
| 11 | Firmware base : réception, validation CRC, sortie USB | `area:base` | Purge des paquets de mauvaise taille. |
| 12 | Trame de lien : RSSI/SNR et taux de pertes | `area:base` | Séparée de la trame de télémétrie. |

## M3 PC + parseur

| # | Tâche | Label | Détail |
|---|---|---|---|
| 13 | Parseur C# + tests contre le vecteur de référence | `area:pc` | Aligner FrameParser.cs avec docs/protocol.md. |
| 14 | Logger CSV série (serial_logger.py) | `area:pc` | Horodatage PC, détection de pertes via seq. |
| 15 | Mesurer la latence bout en bout | `area:pc` | Test T7. |

## M4 Dashboard v1

| # | Tâche | Label | Détail |
|---|---|---|---|
| 16 | Initialiser le projet Unity (LTS, Personal) | `area:unity` | Voir pc/unity/README.md. .NET Framework, Force Text. |
| 17 | SerialReader thread + TelemetryStore | `area:unity` | Support TCP pour fake_base.py et SerialPort pour la base réelle. |
| 18 | Jauges RPM, TPS, températures, lambda, tension | `area:unity` | Style lisible en plein soleil. |
| 19 | Graphiques temps réel et historique | `area:unity` | Fenêtre glissante configurable. |
| 20 | Alertes et état du lien (données périmées, CAN timeout) | `area:unity` | Test T12. |
| 21 | Enregistrement et relecture de session | `area:unity` | Export CSV compatible avec le logger Python. |

## M5 Intégration voiture

| # | Tâche | Label | Détail |
|---|---|---|---|
| 22 | Alimentation voiture : buck, fusible, TVS, ferrite | `area:hardware` | Test T9 (9-16 V, coupures, transitoires). |
| 23 | Montage mécanique et implantation de l'antenne | `area:hardware` | Antenne dégagée du carbone et du métal. |
| 24 | Activer et tester le watchdog | `area:car` | Reprise < 2 s après blocage. |
| 25 | Test de portée 100 m+ voiture montée | `area:test` | Test T6, noter RSSI/SNR. |

## M6 Fiabilisation

| # | Tâche | Label | Détail |
|---|---|---|---|
| 26 | Concevoir un PCB dédié ou migrer vers une carte intégrée | `area:hardware` | Remplacer l'assemblage de modules. |
| 27 | Essais vibrations, chaleur et endurance | `area:test` | Tests T10, T11. |
| 28 | Documentation finale et release v1.0 | `area:docs` | Tag, firmware binaire, configuration, guide de montage. |
