# Dashboard Unity

**Version** : Unity Hub + dernière LTS, licence **Personal** (gratuite sous le seuil de revenus/financement défini par Unity, à vérifier sur leur site).

## Initialisation
1. Unity Hub > New project > template *2D (URP)* ou *3D* > emplacement : **ce dossier** (`pc/unity/`).
2. Project Settings > Player > *Api Compatibility Level* = **.NET Framework** (nécessaire pour `System.IO.Ports`).
3. Commiter `Assets/`, `Packages/`, `ProjectSettings/` (le `.gitignore` exclut `Library/`, `Temp/`, etc.).
4. Activer *Visible Meta Files* et *Force Text* (Project Settings > Editor).

## Architecture prévue
```
SerialReader (thread)  ──bytes──►  FrameParser  ──TelemetryData──►  TelemetryStore (dernier état + historique)
                                                                           │
                                                      Dashboard UI (jauges RPM, TPS, températures, lambda, tension)
                                                      Graphiques temps réel · Alertes · Enregistrement CSV
```
- `Assets/Scripts/FrameParser.cs` : fourni, aligné sur le protocole v1.
- A écrire : `SerialReader.cs` (SerialPort ou TcpClient vers `fake_base.py`), `TelemetryStore.cs`, scènes UI.
- Lecture série sur un **thread séparé**, transfert vers le thread principal via une file concurrente.
- Développement sans hardware : `python pc/tools/fake_base.py --tcp 5555`.
