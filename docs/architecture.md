# Architecture

```
┌─────────── VOITURE ───────────┐        ┌──────── STAND ────────┐
│ MaxxECU ─CAN─► MCP2515 ─SPI─► │        │                       │
│                  Nano         │  868   │  LoRa ─SPI─► Nano     │──USB──► PC
│                  └─SPI─► LoRa ├~~~~~~~►│                       │         ├─ Unity (dashboard)
└───────────────────────────────┘        └───────────────────────┘         └─ outils Python (log, simulateur)
```

## Flux de données
1. ECU émet ses trames CAN (protocole MaxxECU Default) à 500 kbit/s.
2. Le Nano voiture (listen-only) décode les IDs connus (`can_map.h`) et remplit une `TelemetryFrame`.
3. A 10 Hz, la trame (28 octets + CRC) part en LoRa SF7 / 250 kHz.
4. La base valide le CRC et pousse la trame brute sur l'USB série.
5. Unity (ou `serial_logger.py`) re-synchronise, vérifie le CRC, convertit en unités physiques.

## Choix de conception
- **Trame binaire fixe + CRC** : compacte, déterministe, simple à parser sur 3 langages.
- **Décodage CAN sur la voiture** (et pas sur le PC) : on n'émet que l'utile, la bande passante radio reste faible.
- **Pas d'ACK/retransmission** : le temps réel prime, la perte d'une trame est tolérée (`seq` pour mesurer).
- **Simulateur** : permet de développer Unity et les tests sans matériel.

## Marge de bande passante (à mesurer)
Trame 28 octets à 10 Hz : le temps d'émission LoRa SF7/250 kHz est très inférieur à la période de 100 ms (à confirmer par mesure, voir plan de tests). Augmenter SF ou la portée réduit le débit.
