# Mystilink Calculateur BaZi

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## Aperçu

Calcule les cartes BaZi chinoises (Quatre Piliers), les fortunes décennales (DaYun) et les fortunes annuelles (LiuNian). Les résultats sont du JSON structuré adapté aux applications et scripts. Aucune image ni ressource CDN n’est incluse.

## Plateformes et langages

| Cible | Livraison |
|-------|----------|
| Python | Paquet installable `mystilink-bazi-calculator` et CLI `bazi` |
| JavaScript / Node | Paquet npm sous `bindings/js` (lance le CLI ; navigateur via `runCli` injectable) |
| C | En-tête + bibliothèque qui invoque le CLI et renvoie du JSON |
| C++ | Enveloppe légère sur l’API C |
| C# | Enveloppe de processus autour du CLI |
| Java | Enveloppe ProcessBuilder autour du CLI |

Toutes les liaisons non-Python appellent l’exécutable `bazi` sur `PATH` (ou `MYSTILINK_BAZI_CLI`). L’alias long `mystilink-bazi` reste installé pour compatibilité.

## Prérequis

- Python 3.9 ou plus récent
- Pour les liaisons de langage : le CLI doit être installé et disponible sur `PATH`

## Installation et démarrage rapide

```bash
# after obtaining the repository locally
cd mystilink-bazi-calculator
python3 -m pip install -e .
bazi calculate --date 1990-05-15 --hour 12

# optional lunar engine (Python 3.10+)
python3 -m pip install -e '.[lunar]'
bazi calculate --date 1990-05-15 --hour 12 --timezone Asia/Shanghai --calendar-engine lunar
```

Aussi :

```bash
python3 -m mystilink_bazi calculate --date 1990-05-15 --hour 12
```

## CLI

Imprime toujours du JSON sur stdout en cas de succès.

```bash
bazi calculate --date YYYY-MM-DD [--hour N] [--minute N] [--timezone IANA] [--longitude N]
bazi calculate --birth-json path/or/-/inline.json
bazi calculate --calendar-basis path/or/-/basis.json
bazi calculate --date YYYY-MM-DD --hour N --timezone IANA --calendar-engine lunar
bazi dayun --date YYYY-MM-DD --gender male|female [--count N]
bazi liunian --year YYYY [--day-stem STEM] [--pillars-json JSON]
bazi version
```

### calculate

| Option | Description |
|--------|-------------|
| `--date` | Date de naissance `YYYY-MM-DD` (obligatoire sauf `--birth-json` ou `--calendar-basis`) |
| `--hour` | Heure de naissance `0-23` (défaut `11` si omis) |
| `--minute` | Minute de naissance `0-59` (défaut `0`) |
| `--timezone` | Fuseau IANA (temps solaire vrai / moteur lunar / bloc `birth` optionnel) |
| `--longitude` | Longitude en degrés, est positif |
| `--birth-json` | BirthProfile (`mystilink.birth/0.1`) : chemin de fichier, `-` (stdin), ou JSON en ligne |
| `--calendar-engine` | `builtin` (défaut), `lunar` (extra optionnel), ou `external_basis` |
| `--calendar-basis` | JSON calendar-basis / lunar convert externe ; n’importe pas lunar |

Le temps solaire vrai s’applique uniquement lorsque `--timezone` et `--longitude` sont tous deux définis (CLI historique), ou lorsque BirthProfile active `birth.true_solar_time` **et** que fuseau/longitude sont disponibles.

Chaque pilier inclut `stem_index`, `branch_index`, `text`, plus les champs historiques `stem` / `branch` / `ganzhi` (`ganzhi` égale `text`). Le `schema_version` de premier niveau est `mystilink.bazi.chart/0.1` ; `bazi_schema_version` reste `1.0` pour les anciens consommateurs. `calendar_engine` indique `builtin`, `lunar` ou `external_basis`.

### dayun

| Option | Description |
|--------|-------------|
| `--date` | Date de naissance (obligatoire) |
| `--gender` | `male` ou `female` (obligatoire) |
| `--count` | Nombre de périodes décennales (défaut `8`) |

### liunian

| Option | Description |
|--------|-------------|
| `--year` | Année solaire cible (obligatoire) |
| `--day-stem` | Tige du jour pour le libellé des dix dieux (十神) |
| `--pillars-json` | JSON des quatre piliers d’origine pour les indices d’interaction |

## API Python

```python
from datetime import date
from mystilink_bazi import (
    compute_bazi,
    compute_bazi_from_calendar_basis,
    compute_bazi_with_lunar,
    compute_dayun,
    compute_liunian,
)

pillars = compute_bazi(date(1990, 5, 15), hour_interval=12, minute=0)
# optional: compute_bazi_with_lunar(..., timezone="Asia/Shanghai")
# optional: compute_bazi_from_calendar_basis(basis_dict)
dayun = compute_dayun(date(1990, 5, 15), "male", count=8)
liunian = compute_liunian(2024, day_stem=pillars["pillars"]["day"]["stem"])
```

## Compatibilité

- Installation seule : aucune dépendance dure à `mystilink-lunar` ou aux paquets metaphysics-schema.
- Lunar optionnel : `pip install 'mystilink-bazi-calculator[lunar]'` (nécessite Python 3.10+).
- Orchestration sans import : `mystilink-lunar convert ... --json` → `mystilink-bazi calculate --calendar-basis …`.
- Alignement de contrat : les champs de sortie correspondent à `mystilink.bazi.chart/0.1` / formes Ganzhi ; l’entrée BirthProfile suit uniquement la convention de champs `mystilink.birth/0.1`.
- Voir [CHANGELOG.md](../../CHANGELOG.md).

## Exemples

Des exemples exécutables se trouvent sous `examples/{c,cpp,csharp,java,js,node,python}/`. Les sources des liaisons sont sous `bindings/`.

Les schémas des formes JSON CLI sont dans `schema/`. Échantillons :

- BirthProfile : `tests/fixtures/birth.profile.v0.json`
- Calendar basis : `tests/fixtures/calendar.basis.v0.json`

```bash
bazi calculate --birth-json tests/fixtures/birth.profile.v0.json
bazi calculate --calendar-basis tests/fixtures/calendar.basis.v0.json
```


L’option `--envelope` enveloppe le résultat en `mystilink.envelope/0.1` (par défaut : JSON nu).

## Limites

- Les dates de termes solaires pour l’âge de début DaYun utilisent des jours civils approximatifs, pas une précision d’éphéméride.
- Le temps solaire vrai utilise l’équation du temps plus la longitude ; la précision dépend des entrées de fuseau et de longitude.
- Ce paquet ne fournit ni polices, ni images, ni recherches d’assets distants.
- Les règles calendaires intégrées sont approximatives ; elles ne remplacent pas une bibliothèque lunaire/éphéméride dédiée.

## Licence

MIT. Voir [LICENSE](../../LICENSE).

## Retours

Signalez les défauts avec : version CLI (`mystilink-bazi version`), ligne de commande exacte (dates fictives uniquement), et JSON stderr/stdout.
