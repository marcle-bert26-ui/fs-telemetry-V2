# Plan de tests

## Tests logiciels Python

| ID | Test | Moyen | Critère |
|---|---|---|---|
| T1 | CRC, encodage et décodage de trame | `tests/protocol/` + vecteur de référence | CRC correct et valeurs aller-retour identiques |
| T2 | Resynchronisation du flux | `tests/protocol/` | trames valides retrouvées après du bruit |
| T12 | Dashboard Python | `tests/dashboard/` | valeurs et états affichés correctement |
| T13 | Enregistrement / relecture CSV | `tests/dashboard/` | trames enregistrées puis relues sans perte de champs |

La CI exécute uniquement ces tests logiciels. Elle ne compile pas et ne simule pas le firmware Arduino; la validation CAN et matérielle est effectuée séparément sur banc.

## Tests sur banc et véhicule

| ID | Test | Moyen | Critère |
|---|---|---|---|
| T3 | Lecture CAN sur banc | MaxxECU + MTune, listen-only | IDs attendus reçus, ECU non perturbée |
| T4 | Décodage des valeurs | Comparaison MTune / télémétrie | écart dans la résolution ECU |
| T5 | Liaison radio banc | 2 modules à 3 m | 0 % pertes sur 10 min |
| T6 | Portée | Antenne installée, voiture à 100 m+ | pertes < 5 %, noter RSSI/SNR |
| T7 | Latence bout en bout | horodatage `t_ms` vs arrivée PC | < 300 ms |
| T8 | Perte ECU | débrancher le CAN | `FLAG_CAN_TIMEOUT` < 1 s |
| T9 | Alimentation | 9 V à 16 V + coupures + transitoires | pas de reset ; reprise < 2 s |
| T10 | Vibrations / chaleur | essai roulage | aucune coupure |
| T11 | Endurance | 1 h+ moteur tournant | pas de dérive ni de blocage |
