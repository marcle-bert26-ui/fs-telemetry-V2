# Contribuer

## Workflow (GitHub Flow)
1. `main` est toujours compilable et protégée (PR + 1 review + CI verte).
2. Une branche par issue : `feat/12-can-decode`, `fix/20-crc`, `docs/5-protocol`.
3. Commits en **Conventional Commits** : `feat(car): décode RPM`, `fix(base): timeout radio`, `docs: ...`.
4. Ouvrir une PR liée à l'issue (`Closes #12`), remplir le template, attendre la CI.
5. Merge en *squash*.

## Règles de code (C/C++ embarqué)
- Pas d'allocation dynamique (`new`, `malloc`, `String`) dans les firmwares.
- Pas de `delay()` bloquant dans la boucle principale : utiliser `millis()`.
- Constantes et brochages dans `config.h`, jamais en dur.
- Toute modification de la trame → mettre à jour `docs/protocol.md`, `telemetry_frame.h`, `FrameParser.cs`, `tests/` **dans la même PR** et incrémenter `PROTOCOL_VERSION`.
- Watchdog actif en permanence sur le firmware voiture.

## Définition of Done
- Compile en CI, testé sur banc si matériel concerné, doc à jour, revue approuvée.
