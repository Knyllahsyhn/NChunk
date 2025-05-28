
# NChunk – Async Chunked Uploader for Nextcloud

**NChunk** uploads huge files to Nextcloud safely—no browser, no time‑outs.

* 🏎 **Fully async** (`aiohttp` + `aiofiles`) — one connection, full speed
* 🔀 **Chunk upload** (≥ 5 MiB) with automatic merge (`MOVE …/.file`)
* 🖥 **Typer CLI** — self‑documenting, with colorized Rich output
* 📊 **Live progress bars** (speed, ETA, multiple files in parallel)
* 🔐 Secure credential storage (keyring) + `.env` fallback, **login check**
* 👥 **Profiles** for multiple clouds / accounts
* Requires **Python ≥ 3.11** • MIT License

---

## Table of Contents
1. [Installation](#installation)  
2. [First Login](#first-login)  
3. [Upload Files](#upload-files)  
4. [Options & Examples](#options--examples)  
5. [Profiles](#profiles)  
6. [Development & Tests](#development--tests)  
7. [Roadmap](#roadmap)  
8. [License](#license)  

---

## Installation

```bash
# recommended: src-layout + editable install
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
pip install -e .[dev]                # incl. pytest + ruff
```

(Once on PyPI you can simply run `pip install nchunk`.)

---

## First Login

```bash
# instantly verifies URL + credentials via PROPFIND
nchunk login https://cloud.example.com alice
# password is prompted securely
```

* On success credentials are stored in the OS keyring (`nchunk_nextcloud`).  
* On failure you get a clear message and **nothing** is saved.

---

## Upload Files

```bash
# single file
nchunk upload movie.iso                 \
       --url https://cloud.example.com  \
       --user alice

# several in parallel
nchunk upload *.zip docs/**/*.pdf       \
       --url cloud.example.com          \
       --user alice                     \
       --chunk-size 10485760            \
       --remote-dir Backups/$(date +%Y-%m-%d)
```

> You may omit `https://`; the tool auto‑attaches `/remote.php/dav` if needed.

---

## Options & Examples

| Flag            | Default    | Description                                    |
|-----------------|------------|------------------------------------------------|
| `--chunk-size`  | `10485760` | bytes per chunk (≥ 5 MiB)                      |
| `--remote-dir`  | `""`       | target folder in Nextcloud (created if absent) |
| `--insecure`    | `False`    | skip TLS verification (self‑signed certs)      |
| `--concurrency` | `4`        | max concurrent file uploads                    |
| `--profile`     | `default`  | separate multiple accounts                     |
| `--resume`*     | –          | *planned* — resume aborted upload              |
| `--dry-run`*    | –          | *planned* — print requests, do nothing         |

---

## Profiles

```bash
# Work cloud
nchunk login https://cloud.work.com alice --profile work

# Private cloud
nchunk login cloud.home.net bob --profile home

# Use explicit profile
nchunk upload video.mp4 --profile work
```

Credentials are stored under `<url>::<user>::<profile>`.

---

## Development & Tests

```bash
ruff check src tests      # static analysis
pytest -q                 # unit + async tests
```

The **src‑layout** ensures imports work only after  
`pip install -e .` — missing metadata show up immediately.

---

## Roadmap

- [ ] **Resume** aborted uploads (`--resume`)
- [ ] **Folder sync** (watch & upload)
- [ ] Progress export as JSON / quiet mode
- [ ] Signed wheels + PyPI release
- [ ] Windows single‑binary (pex / shiv)

PRs & issues welcome 🙂

---

## License

MIT — see [`LICENSE`](LICENSE).
