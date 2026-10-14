# Protocole de télémétrie v1

Liaison voiture → base : **1 trame binaire de 28 octets**, little-endian, envoyée à 10 Hz.
La base la retransmet **telle quelle** sur l'USB série (115200 bauds). Le PC se re-synchronise sur `A5 5A` et recontrôle le CRC.

| Offset | Taille | Champ | Type | Unité / échelle |
|---|---|---|---|---|
| 0 | 1 | sync0 | u8 | `0xA5` |
| 1 | 1 | sync1 | u8 | `0x5A` |
| 2 | 1 | version | u8 | `1` |
| 3 | 1 | seq | u8 | compteur circulaire |
| 4 | 4 | t_ms | u32 | ms (millis voiture) |
| 8 | 2 | rpm | u16 | tr/min |
| 10 | 2 | tps_d | u16 | 0,1 % |
| 12 | 2 | map_dkpa | u16 | 0,1 kPa |
| 14 | 2 | lambda_m | u16 | 0,001 λ |
| 16 | 2 | vbat_c | u16 | 0,01 V |
| 18 | 2 | clt_d | i16 | 0,1 °C (eau) |
| 20 | 2 | iat_d | i16 | 0,1 °C (air) |
| 22 | 2 | egt | i16 | 1 °C |
| 24 | 2 | flags | u16 | bit0 CAN timeout, bit1 ECU alive, bit2 batterie faible |
| 26 | 2 | crc | u16 | CRC-16/CCITT-FALSE sur les octets 2 à 25 |

- **Valeur absente** : `0xFFFF` (u16) ou `0x8000` (i16).
- **Pertes** : calculées côté PC via `seq` (saut de compteur).
- **CRC** : poly `0x1021`, init `0xFFFF`, sans réflexion, xorout `0`. Contrôle : CRC("123456789") = `0x29B1`.

## Vecteur de test (identique en C, Python et C#)
Entrée : seq=1, t_ms=1000, rpm=8000, tps=50,0 %, MAP=100,0 kPa, λ=1,000, vbat=13,80 V, clt=90,0 °C, iat=35,0 °C, egt=700 °C, flags=2.

```
A55A0101E8030000401FF401E803E803640584035E01BC020200E5BF
```

(Vérifié : sortie identique entre `telemetry_frame.h` compilé en C++ et `pc/tools/protocol.py`.)

## Règle d'évolution
Modifier la trame = nouvelle `PROTOCOL_VERSION`, mise à jour de ce fichier, de `telemetry_frame.h`, `protocol.py`, `FrameParser.cs` et du vecteur de test, dans la même PR.

## Côté ECU (CAN) : à compléter
Les CAN ID, offsets et échelles du protocole *MaxxECU Default* sont à relever dans la doc officielle et à confirmer par sniffing du bus (issue « Identifier les CAN ID MaxxECU »). Rien n'est supposé dans le code tant que ce n'est pas validé (`can_map.h`).
