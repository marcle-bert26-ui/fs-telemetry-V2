# Plan projet

## Objectif
Télémétrie temps réel (≥ 10 Hz, portée ≥ 100 m, faible consommation) de la MaxxECU Sport vers un dashboard Unity au stand.

## Rôles (à nommer)
| Rôle | Responsable |
|---|---|
| Chef de projet / intégration | |
| Firmware voiture (CAN + radio) | |
| Hardware / alimentation / câblage | |
| Firmware base + outils PC | |
| Unity / UI | |
| Validation / tests | |

## Jalons (durées indicatives, à ajuster au calendrier de l'équipe)
| Jalon | Contenu | Livrable / critère de sortie |
|---|---|---|
| **M0 Setup** | Repo, CI, conventions, matériel commandé | CI verte sur `main` |
| **M1 CAN banc** | Lecture MaxxECU, IDs relevés | Tableau IDs validé (T3) |
| **M2 Trame + radio** | Trame v1, lien LoRa | T1, T5 OK |
| **M3 PC + parseur** | Base, parseur C#, logger CSV | Données lues sur PC (T2, T7) |
| **M4 Dashboard v1** | Jauges, graphes, alertes, simulateur | Démo avec `fake_base.py` (T12) |
| **M5 Intégration voiture** | Montage, alim, antenne | T6, T8, T9 OK |
| **M6 Fiabilisation** | Vibrations, endurance, doc finale | T10, T11 OK, PCB/boîtier figé |

## Chemin critique
Matériel (délais) → IDs CAN MaxxECU → décodage → trame → intégration. Le dashboard Unity avance **en parallèle** grâce au simulateur.

## Registre de risques
| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Niveaux 5 V/3,3 V sur SPI partagé | Moyenne | Matériel détruit | Level-shifter, contrôle multimètre |
| Quartz MCP2515 ≠ config | Élevée | CAN muet | Vérifier le module, constante `CAN_MCP_CLOCK` |
| IDs CAN mal interprétés | Moyenne | Données fausses | Sniffing + comparaison MTune |
| Perturbation du bus ECU | Faible | Critique | Mode listen-only, test banc |
| Alim polluée / resets | Moyenne | Pertes de données | Buck, TVS, filtre, watchdog |
| Portée insuffisante (carbone) | Moyenne | Liaison coupée | Antenne dégagée, SF plus haut, test à 100 m+ |
| Réglementation radio / règlement FS | Faible | Disqualification | Vérifier tôt |
| Goulot de compétences (1 dev C) | Élevée | Retards | Doc, revues croisées, simulateur |

## Gouvernance
- Point d'équipe hebdomadaire (15 min) : avancement par jalon, blocages.
- Board GitHub Projects : *Backlog → Ready → In progress → Review → Done*.
- Revue de PR obligatoire, CI verte pour merger.
- Gel de version (tag `v1.0`) avant la compétition, avec firmware binaire et config attachés à la release.

## Définition of Done
Voir `CONTRIBUTING.md`.
