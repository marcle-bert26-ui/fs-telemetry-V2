# Plan de tests

| ID | Test | Moyen | Critère |
|---|---|---|---|
| T1 | CRC / trame : C = Python = C# | CI + vecteur de test | identique |
| T2 | Resynchronisation du flux | `tests/` + C# | trames valides retrouvées après bruit |
| T3 | Lecture CAN sur banc | MaxxECU + MTune, listen-only | IDs attendus reçus, ECU non perturbée |
| T4 | Décodage des valeurs | Comparaison MTune / télémétrie | écart dans la résolution ECU |
| T5 | Liaison radio banc | 2 modules à 3 m | 0 % pertes sur 10 min |
| T6 | Portée | Antenne installée, voiture à 100 m+ | pertes < 5 %, noter RSSI/SNR |
| T7 | Latence bout en bout | horodatage `t_ms` vs arrivée PC | < 300 ms |
| T8 | Perte ECU | débrancher le CAN | `FLAG_CAN_TIMEOUT` < 1 s |
| T9 | Alimentation | 9 V à 16 V + coupures + transitoires | pas de reset ; reprise < 2 s |
| T10 | Vibrations / chaleur | essai roulage | aucune coupure |
| T11 | Endurance | 1 h+ moteur tournant | pas de dérive ni de blocage |
| T12 | UI Unity | simulateur avec pertes/corruption | aucune exception, affichage « données périmées » |
