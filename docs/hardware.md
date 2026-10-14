# Hardware

## Voiture
| Élément | Choix | Notes |
|---|---|---|
| MCU | Arduino Nano (ATmega328P) | validation ; migration possible vers Feather M4 CAN ou PCB dédié |
| CAN | Module MCP2515 + TJA1050 | **vérifier le quartz (8/16 MHz)** et le reporter dans `CAN_MCP_CLOCK` |
| Radio | Module SX1276/RFM95 868 MHz | 3,3 V |
| Antenne | Quart d'onde ~8,6 cm, dégagée du carbone/métal | tester installée dans la voiture |
| Alim | Buck 12 V → 5 V + fusible + TVS + ferrite | alimenter le 5 V, pas la broche Vin |

## Station de base
Nano + module LoRa 868 MHz + câble USB vers le PC. Pas besoin de CAN.

## Branchement CAN (MaxxECU Sport)
- CAN H = pin **E1**, CAN L = pin **E2** du connecteur principal 48 pts (paire torsadée gris/rose).
- Bitrate **500 kbit/s**, protocole de sortie par défaut activé dans MTune, redémarrer l'ECU après changement.
- Terminaison : 120 Ω à chaque extrémité du bus uniquement ; la MaxxECU a une terminaison intégrée, ajouter une 120 Ω externe seulement si le bus dépasse ~1 m (à valider sur banc).
- Récepteur en **listen-only** : le module ne doit jamais acquitter ni émettre.

## ⚠ Point d'attention : niveaux logiques sur le SPI partagé
Le MCP2515 (5 V) et le module LoRa (3,3 V) partagent MOSI/MISO/SCK. Le MISO 5 V du MCP2515 **peut détruire** la broche MISO du LoRa.
**Solution** : placer le module LoRa derrière un level-shifter 4 voies (BSS138 ou équivalent) sur SCK, MOSI, MISO, CS, et RST via diviseur/shifter. Alternative : choisir un module MCP2515 + transceiver 3,3 V (SN65HVD230) et alimenter le tout en 3,3 V.
A valider au multimètre avant la première mise sous tension.

## Brochage Nano (voiture)
| Fonction | Broche |
|---|---|
| SPI SCK / MISO / MOSI | D13 / D12 / D11 |
| CAN CS / INT | D10 / D2 |
| LoRa CS / RST / DIO0 | D8 / D9 / D3 |

## Robustesse
Soudures directes ou borniers à verrouillage (pas de Dupont), fixation anti-vibrations, vernis de protection, watchdog actif, implantation loin de l'échappement et des câbles HT.
Consulter le règlement Formula Student de l'année (circuit basse tension, fusibles, règles radio).

## Réglementation radio
868 MHz : respecter puissance max et duty cycle de la sous-bande utilisée. A vérifier avant la compétition.
