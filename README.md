# NChunk – Nextcloud Chunk Uploader (Async + Rich CLI)

Upload große Dateien **bruchsicher** nach Nextcloud – ohne Browser-Timeouts.

* **Asynchron (aiohttp + aiofiles)** – eine Session, volle Leitung
* **Chunk-Upload** (≥ 5 MiB) mit automatischem Zusammenführen (`MOVE …/.file`)
* **Typer CLI** – selbstdokumentierend, Farben via Rich
* **Schicke Fortschrittsbalken** (Speed, ETA, mehrere Dateien parallel)
* **Keyring**‑Integration & `.env`‑Fallback, **Login‑Check** beim Speichern
* **Profile** für mehrere Clouds / Accounts
* Python ≥ 3.11 • GPLV3

---
![PyPI](https://img.shields.io/pypi/v/nchunk)
![CI](https://github.com/Knyllahsyhn/nchunk/actions/workflows/ci.yml/badge.svg)
[![Release to PyPI & GitHub](https://github.com/Knyllahsyhn/NChunk/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/Knyllahsyhn/NChunk/actions/workflows/release.yml)

## Inhaltsverzeichnis

1. [Installation](#installation)
2. [Erster Login](#erster-login)
3. [Dateien hochladen](#dateien-hochladen)
4. [Optionen &amp; Beispiele](#optionen--beispiele)
5. [Profile – mehrere Accounts](#profile--mehrere-accounts)
6. [Entwicklung &amp; Tests](#entwicklung--tests)
7. [Roadmap](#roadmap)
8. [Lizenz](#lizenz)

---

## Installation

```bash
# empfohlenes src‑Layout → editable install
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\Activate.ps1
pip install -e .[dev]               # inkl. pytest & ruff
```

Oder später direkt aus PyPI:

```bash
pip install nchunk
```

---

## Erster Login

```bash
# prüft URL + Zugangsdaten sofort per PROPFIND
nchunk login https://cloud.example.com alice
# Passwort‑Eingabe wird verdeckt
```

* Erfolgreich → Daten landen verschlüsselt im OS‑Keyring (`nchunk_nextcloud`).
* Fehlgeschlagen → klare Meldung, **keine** Speicherung.

---

## Dateien hochladen

```bash
# Ein File
nchunk upload movie.iso                 \
       --url https://cloud.example.com  \
       --user alice

# Mehrere parallel
nchunk upload *.zip docs/**/*.pdf       \
       --url cloud.example.com          \
       --user alice                     \
       --chunk-size 10485760            \
       --remote-dir Backups/$(date +%Y-%m-%d)
```

> `--url` kann mit oder ohne `https://` angegeben werden; das Tool hängt
> bei Bedarf `/remote.php/dav` automatisch an.

---

## Optionen & Beispiele

| Flag              | Default      | Erklärung                                    |
| ----------------- | ------------ | --------------------------------------------- |
| `--chunk-size`  | `10485760` | Bytes pro Chunk (≥ 5 MiB)                  |
| `--remote-dir`  | `""`       | Zielordner in Nextcloud (wird angelegt)       |
| `--insecure`    | `False`    | TLS‑Prüfung abschalten (Self‑Signed Certs) |
| `--concurrency` | `4`        | Max. parallele Datei‑Uploads                 |
| `--profile`     | `default`  | Trennt mehrere Accounts (siehe unten)         |
| `--resume`*     | –           | *geplant* – Upload fortsetzen              |
| `--dry-run`*    | –           | *geplant* – nur Requests anzeigen          |

---

## Profile – mehrere Accounts

```bash
# Work‑Cloud
nchunk login https://cloud.work.com alice --profile work

# Private Cloud
nchunk login cloud.home.net bob --profile home

# Upload mit explizitem Profil
nchunk upload video.mp4 --profile work
```

Keyring‑Keys → `<url>::<user>::<profile>`.

---

## Entwicklung & Tests

```bash
ruff check src tests   # Linting
pytest                 # Unit‑ & Async‑Tests
```

Der **src‑Layer** stellt sicher, dass Tests nur nach
`pip install -e .` funktionieren – Import‑Fehler fallen sofort auf.

---

## Roadmap

- [ ] **Resume** abgebrochener Uploads (`--resume`)
- [ ] **Sync‑Ordner** (watch & upload)
- [ ] Progress‑Export als JSON / Quiet‑Mode
- [ ] PyPI‑Release mit Signed Wheels
- [ ] Windows‑Installer (pex / shiv)

PRs & Issues willkommen 🙂

---

## Lizenz

GPLV3, siehe LICENSE
