# Protocole de télémétrie cible v1

La liaison prévue voiture → base utilise **1 trame binaire de 28 octets**, little-endian, envoyée à 10 Hz. La base la retransmet **telle quelle** sur l'USB série (115200 bauds). Le PC se re-synchronise sur `A5 5A` et recontrôle le CRC. Cette spécification est utilisée par le logiciel PC et son simulateur; le sketch Arduino actuel affiche du texte série et n'implémente pas encore ce transport.

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

## Vecteur de test
Entrée : seq=1, t_ms=1000, rpm=8000, tps=50,0 %, MAP=100,0 kPa, λ=1,000, vbat=13,80 V, clt=90,0 °C, iat=35,0 °C, egt=700 °C, flags=2.

```
A55A0101E8030000401FF401E803E803640584035E01BC020200E5BF
```

Ce vecteur est vérifié par les tests Python du protocole. Le sketch Arduino voiture actuel lit les trames CAN `0x600` et `0x601` puis affiche les valeurs sur le port série; il ne produit pas encore cette trame binaire.

## Règle d'évolution
Modifier la trame = nouvelle `PROTOCOL_VERSION`, mise à jour de ce fichier, de `pc/python/telemetry/protocol.py`, des parseurs PC concernés et du vecteur de test, dans la même PR. Lorsqu'un transport binaire Arduino sera réintroduit, sa sérialisation et ses tests devront aussi être mis à jour.

## Côté ECU (CAN) : tension batterie

Le firmware voiture reprend la configuration de référence du document MaxxECU Sport fourni :

| Paramètre | Valeur initiale |
|---|---|
| ID de sortie | `0x601`, standard |
| Débit de sortie conseillé dans MTune | 10 Hz |
| Valeur | `Battery voltage`, Data value 1 |
| Position | octets 0-1 |
| Type / endianness | unsigned 16 bits, little-endian |
| Conversion vers `vbat_c` | valeur CAN × 1 / 1 + 0 centivolt |

Le sketch Arduino voiture actuel lit `0x601` comme une trame little-endian et affiche ses quatre valeurs brutes; la conversion vers `vbat_c` et la transmission PC/LoRa décrites ci-dessus ne sont pas implémentées dans ce sketch. La formule de conversion prévue pour le protocole est :

```
vbat_c = raw × CAN_BATTERY_SCALE_NUMERATOR
         / CAN_BATTERY_SCALE_DENOMINATOR
         + CAN_BATTERY_OFFSET_CV
```

La valeur initiale suppose que la valeur brute est déjà en centivolts (ex. `1380` pour `13,80 V`). Le document MaxxECU précise que les réglages multiplicateur/diviseur/offset sont à calibrer : comparer la valeur reçue avec MTune, puis régler ces paramètres et/ou la formule de sortie dans MTune. Vérifier également dans MTune l'ID, le type standard, l'ordre little-endian et le contenu de Data value 1 avant utilisation réelle. La configuration logicielle n'est pas une validation sur véhicule.

La validation du décodage CAN et des valeurs reçues se fait sur matériel; elle n'est pas couverte par la suite CI logicielle.
