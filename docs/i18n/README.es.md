# Mystilink Calculadora BaZi

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## Resumen

Calcula cartas BaZi chinas (Cuatro Pilares), fortunas decenales (DaYun) y fortunas anuales (LiuNian). Los resultados son JSON estructurado apto para aplicaciones y scripts. No se incluyen imágenes ni recursos CDN.

## Plataformas e idiomas

| Objetivo | Entrega |
|----------|----------|
| Python | Paquete instalable `mystilink-bazi-calculator` y CLI `bazi` |
| JavaScript / Node | Paquete npm bajo `bindings/js` (lanza el CLI; navegador vía `runCli` inyectable) |
| C | Cabecera + biblioteca que invoca el CLI y devuelve JSON |
| C++ | Envoltorio ligero sobre la API C |
| C# | Envoltorio de proceso sobre el CLI |
| Java | Envoltorio ProcessBuilder sobre el CLI |

Todos los enlaces no Python llaman al ejecutable `bazi` en `PATH` (o `MYSTILINK_BAZI_CLI`). El alias largo `mystilink-bazi` sigue instalándose por compatibilidad.

## Requisitos

- Python 3.9 o superior
- Para enlaces de lenguaje: el CLI debe estar instalado y disponible en `PATH`

## Instalación e inicio rápido

```bash
# after obtaining the repository locally
cd mystilink-bazi-calculator
python3 -m pip install -e .
bazi calculate --date 1990-05-15 --hour 12

# optional lunar engine (Python 3.10+)
python3 -m pip install -e '.[lunar]'
bazi calculate --date 1990-05-15 --hour 12 --timezone Asia/Shanghai --calendar-engine lunar
```

También:

```bash
python3 -m mystilink_bazi calculate --date 1990-05-15 --hour 12
```

## CLI

Siempre imprime JSON en stdout en caso de éxito.

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

| Opción | Descripción |
|--------|-------------|
| `--date` | Fecha de nacimiento `YYYY-MM-DD` (obligatoria salvo `--birth-json` o `--calendar-basis`) |
| `--hour` | Hora de nacimiento `0-23` (predeterminado `11` si se omite) |
| `--minute` | Minuto de nacimiento `0-59` (predeterminado `0`) |
| `--timezone` | Zona IANA (tiempo solar verdadero / motor lunar / bloque `birth` opcional) |
| `--longitude` | Longitud en grados, este positivo |
| `--birth-json` | BirthProfile (`mystilink.birth/0.1`): ruta de archivo, `-` (stdin), o JSON en línea |
| `--calendar-engine` | `builtin` (predeterminado), `lunar` (extra opcional), o `external_basis` |
| `--calendar-basis` | JSON calendar-basis / lunar convert externo; no importa lunar |

El tiempo solar verdadero solo se aplica cuando `--timezone` y `--longitude` están ambos definidos (CLI legado), o cuando BirthProfile activa `birth.true_solar_time` **y** zona/longitud están disponibles.

Cada pilar incluye `stem_index`, `branch_index`, `text`, más los campos legados `stem` / `branch` / `ganzhi` (`ganzhi` es igual a `text`). El `schema_version` de nivel superior es `mystilink.bazi.chart/0.1`; `bazi_schema_version` permanece `1.0` para consumidores antiguos. `calendar_engine` indica `builtin`, `lunar` o `external_basis`.

### dayun

| Opción | Descripción |
|--------|-------------|
| `--date` | Fecha de nacimiento (obligatoria) |
| `--gender` | `male` o `female` (obligatorio) |
| `--count` | Número de períodos decenales (predeterminado `8`) |

### liunian

| Opción | Descripción |
|--------|-------------|
| `--year` | Año solar objetivo (obligatorio) |
| `--day-stem` | Tallo del día para etiquetar los diez dioses (十神) |
| `--pillars-json` | JSON de los cuatro pilares originales para pistas de interacción |

## API de Python

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

## Compatibilidad

- Instalación sola: sin dependencia dura de `mystilink-lunar` ni de paquetes metaphysics-schema.
- Lunar opcional: `pip install 'mystilink-bazi-calculator[lunar]'` (requiere Python 3.10+).
- Orquestación sin import: `mystilink-lunar convert ... --json` → `mystilink-bazi calculate --calendar-basis …`.
- Alineación de contrato: los campos de salida coinciden con `mystilink.bazi.chart/0.1` / formas Ganzhi; la entrada BirthProfile sigue solo la convención de campos `mystilink.birth/0.1`.
- Véase [CHANGELOG.md](../../CHANGELOG.md).

## Ejemplos

Las muestras ejecutables están en `examples/{c,cpp,csharp,java,js,node,python}/`. Las fuentes de enlaces están en `bindings/`.

Los esquemas de formas JSON del CLI están en `schema/`. Muestras:

- BirthProfile: `tests/fixtures/birth.profile.v0.json`
- Calendar basis: `tests/fixtures/calendar.basis.v0.json`

```bash
bazi calculate --birth-json tests/fixtures/birth.profile.v0.json
bazi calculate --calendar-basis tests/fixtures/calendar.basis.v0.json
```


La opción `--envelope` envuelve el resultado como `mystilink.envelope/0.1` (por defecto sigue siendo JSON desnudo).

## Límites

- Las fechas de términos solares para la edad de inicio de DaYun usan días civiles aproximados, no precisión de efemérides.
- El tiempo solar verdadero usa la Ecuación del Tiempo más la longitud; la precisión depende de las entradas de zona y longitud.
- Este paquete no incluye tipografías, imágenes ni búsquedas de recursos remotos.
- Las reglas de calendario integradas son aproximadas; no sustituyen una biblioteca lunar/efemérides dedicada.

## Licencia

MIT. Véase [LICENSE](../../LICENSE).

## Comentarios

Informe defectos con: versión CLI (`mystilink-bazi version`), línea de comando exacta (solo fechas ficticias) y JSON stderr/stdout.
