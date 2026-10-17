# Architecture cible

```
┌─────────── VOITURE ───────────┐        ┌──────── STAND ────────┐
│ MaxxECU ─CAN─► MCP2515 ─SPI─► │        │                       │
│                  Nano         │  868   │  LoRa ─SPI─► Nano     │──USB──► PC
│                  └─SPI─► LoRa ├~~~~~~~►│                       │         ├─ Dashboard Python (V1)
└───────────────────────────────┘        └───────────────────────┘         └─ Unity (étape suivante)
```

## Flux prévu
1. ECU émet ses trames CAN (protocole MaxxECU Default) à 500 kbit/s.
2. Le Nano voiture (listen-only) décode les IDs connus et remplit une trame de télémétrie.
3. A 10 Hz, la trame (28 octets + CRC) part en LoRa SF7 / 250 kHz.
4. La base valide le CRC et pousse la trame brute sur l'USB série.
5. `pc/python/telemetry/` re-synchronise, vérifie le CRC, convertit en unités physiques et gère l'enregistrement/relecture CSV; `pc/python/ui/` affiche les données dans le dashboard Python. Le code Unity reste isolé dans `pc/unity/`.

## État actuel
Le sketch `arduino/car/CAN/CAN.ino` lit les IDs CAN `0x600` et `0x601`, puis affiche les valeurs décodées sur le port série. Il ne construit ni n'envoie encore la trame binaire de télémétrie. Le dossier Arduino base ne contient pas encore de firmware; le dashboard et le protocole Python se testent indépendamment avec le simulateur. La liaison complète voiture → stand → PC reste donc à intégrer et à valider sur matériel.

## Choix de conception
- **Trame binaire fixe + CRC** (cible) : compacte, déterministe, simple à parser.
- **Décodage CAN sur la voiture** : on vise à n'émettre que l'utile, pour limiter la bande passante radio.
- **Pas d'ACK/retransmission** : le temps réel prime, la perte d'une trame est tolérée (`seq` pour mesurer).
- **Simulateur** : permet de développer le dashboard et les tests logiciels sans matériel.

## Marge de bande passante (à mesurer)
Trame 28 octets à 10 Hz : le temps d'émission LoRa SF7/250 kHz est très inférieur à la période de 100 ms (à confirmer par mesure, voir plan de tests). Augmenter SF ou la portée réduit le débit.
