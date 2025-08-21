# TC-C2PA-PY

[![Build](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/build_image.yml/badge.svg)](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/build_image.yml)
[![Unit Tests](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/run_unit_tests.yml/badge.svg)](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/run_unit_tests.yml)
[![Lint](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/lint.yml/badge.svg)](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/lint.yml)

---

**TC-C2PA-PY** is an open‑source Python library for constructing **C2PA** Content Credentials manifests that validate with `c2patool` and common C2PA consumers. It supports building **claims, assertions, and COSE signatures** and embedding the manifest store into **JPEG (APP11)** and **PDF (incremental update)** assets.

- **C2PA spec:** https://c2pa.org/  
- **Validation:** https://github.com/content-authenticity-initiative/c2pa-rs (`c2patool`)

> ⚠️ This library helps you build **valid manifests**, but trust decisions (anchors, allow/deny lists, TSA) are **your responsibility**. For production, you must provision a certificate chain anchored to an accepted trust root and configure validation policy accordingly.

---

## Features

- C2PA **Claim** (`c2pa.claim`) with canonical CBOR, `dc:format`, `alg`, and hashed‑URIs for assertions.
- C2PA **Signature** (`c2pa.signature`) using **COSE_Sign1 (PS256)** with **detached** payload and `x5chain` in protected header.
- **Assertion Store** with common assertions (e.g., `c2pa.hash.data` **hard‑binding**, schema.org **CreativeWork**, etc.).
- **Embedding**:
  - **JPEG** via **APP11** segments (size‑driven iterative layout).
  - **PDF** via **incremental update** at EOF (xref/trailer preserved; `/AF` + `/Names/EmbeddedFiles`).  
- Validates with `c2patool` (structure + signatures).

---

## Quick start

### 1) Clone & (optionally) use Dev Containers

- Install Docker and VS Code “Dev Containers” extension.  
- Open the repo in VS Code and **Reopen in Container**. The container installs Python, your package in editable mode, and configures **Ruff** (lint + format on save).

> Dev container also sets Ruff as default formatter and auto‑fixes on save (see `.devcontainer/devcontainer.json`).

### 2) Install locally (without devcontainer)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
python -m pip install pytest ruff
```

### 3) Run tests

```bash
pytest -q
```

### 4) Lint & format

```bash
# check formatting & linting
ruff format --check .
ruff check .

# apply fixes
ruff format .
ruff check . --fix
```

### 5) Try the example apps

- **JPEG:** `test_application/jpeg_test_app.py`  
- **PDF:** `test_application/pdf_test_app.py`  
- **(Legacy note)** Library usage example is also available at: `test_application/test_app.py`

These scripts:
1) Load a sample asset (`tests/fixtures/test_image.jpg` or `tests/fixtures/test_document.pdf`).  
2) Build a manifest:
   - `TC_C2PA_GenerateAssertion` (e.g., **CreativeWork**),
   - `TC_C2PA_GenerateHashDataAssertion` (hard‑binding),
   - `TC_C2PA_GenerateManifest` (claim + signature + store).  
3) Embed the manifest (`TC_C2PA_EmplaceManifest`).  
4) Write a new asset with C2PA.

Validate with:
```bash
c2patool path/to/your_output.jpg
c2patool path/to/your_output.pdf
```

> For trust evaluation (optional), add anchors/policy:
> ```bash
> c2patool your.pdf trust >   --trust_config https://contentcredentials.org/trust/store.cfg >   --trust_anchors https://contentcredentials.org/trust/anchors.pem >   --allowed_list https://contentcredentials.org/trust/allowed.pem
> ```

---

## API overview (high‑level)

```python
from tc_c2pa_py.interface import (
    TC_C2PA_GenerateAssertion,
    TC_C2PA_GenerateHashDataAssertion,
    TC_C2PA_GenerateManifest,
    TC_C2PA_EmplaceManifest,
    C2PA_AssertionTypes,
    C2PA_ContentTypes,
)

# 1) Assertions
creative_work = TC_C2PA_GenerateAssertion(
    C2PA_AssertionTypes.creative_work,
    {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Example Author"}],
    },
)

# Hard‑binding (exclusion starts at original EOF for PDF, or APP11 insert offset for JPEG)
hash_data = TC_C2PA_GenerateHashDataAssertion(
    cai_offset=<offset>,
    hashed_data=<sha256_of_original_asset_bytes>,
)

# 2) Manifest (claim + signature + assertion store)
with open("tests/fixtures/crypto/ps256.pem", "rb") as f:
    private_key = f.read()  # PKCS#8 PEM (RSA PSS)

with open("tests/fixtures/crypto/ps256.pub", "rb") as f:
    cert_chain = f.read()   # PEM bundle (leaf + intermediates)

manifest_store = TC_C2PA_GenerateManifest(
    assertions=[creative_work, hash_data],
    private_key=private_key,
    certificate_chain=cert_chain,
)

# 3) Embed
result_bytes = TC_C2PA_EmplaceManifest(
    C2PA_ContentTypes.pdf,  # or C2PA_ContentTypes.jpg
    content_bytes=<bytes_of_original_asset>,
    c2pa_offset=<offset>,   # for JPEG: insert offset; for PDF: len(original_bytes)
    manifests=manifest_store,
)
```

### Notes for PDF vs JPEG

- **PDF**: we append an **incremental update**. The `c2pa.hash.data` exclusion starts at `len(original_pdf)` and its **length** equals the final tail size (computed iteratively).  
- **JPEG**: we insert **APP11** segments. The exclusion start is the APP11 insertion offset; the length is the final APP11 payload length (also computed iteratively).

The library takes care of iterative sizing so the `c2pa.hash.data` **matches exactly**, otherwise validators return `assertion.dataHash.mismatch`.

---

## How to start this project (VS Code + Dev Containers)

It is recommended to work with existing modules using [Dev containers](https://code.visualstudio.com/docs/devcontainers/containers) in Visual Studio Code.

### Prerequisites

- Install [WSL](https://ubuntu.com/desktop/wsl) (Windows).  
- Install the Docker client ([Windows](https://docs.docker.com/desktop/setup/install/windows-install/) / [Mac](https://docs.docker.com/desktop/setup/install/mac-install/) / [Linux](https://docs.docker.com/desktop/setup/install/linux-install/)).  
  - Make sure Docker client is the latest version.  
  - Make sure Docker uses the **WSL 2** based engine (Windows).

### Open the project

- Make sure Docker daemon is running before opening the dev container.  
  Press `Ctrl + Shift + P` → **Reopen in Container** (or click the bottom‑left button → **Reopen in Container**).
- Microsoft VS Code: ensure the **Dev Containers** extension is installed.  
  Check via **View: Extensions** (`Ctrl + Shift + X`).

### How to run project (VS Code tasks)

There are VSCode tasks provided to interact with code. Use `Ctrl + Shift + B` to open the tasks menu:

- **Run unit tests** — runs all unit tests in the `tests` folder.  
- **Run test application** — runs the usage examples in the `test_application` folder.  
- **Build package** — builds the Python package configured in `setup.py`.

---

## CI: build, lint, and tests

We ship three GitHub Actions (see `.github/workflows/`):

- **CI** (`ci.yml`): build & tests on Python 3.8/3.10/3.12.  
- **Lint** (`lint.yml`): Ruff lint + format checks.  
- **Run unit‑tests** (`run-unit-tests.yml`): containerized unit tests (optional), e.g. using your GHCR image.

Badges at the top reflect their current status.

> If you keep a single‑container “unit‑tests only” workflow, that’s fine: adapt badges and remove duplicates as you prefer.

---

## Dev container

The project includes a `.devcontainer/devcontainer.json` that:

- installs the **Ruff** extension and sets it as **default formatter**,  
- enables **auto‑format** and **auto‑fix on save**,  
- installs `ruff` inside the container so it works offline.

You can also sync these settings locally via `.vscode/settings.json` and `.vscode/extensions.json`.

---

## Certificates & trust

- Example keys live under `tests/fixtures/crypto/`. They are suitable for **development only**.  
- For production:
  - use a real document‑signing certificate (RSA‑PSS or ECDSA per C2PA),  
  - provide a **leaf + intermediates** bundle (no root),  
  - configure trust anchors/allow‑lists in your validator environment.  
- Time‑stamping (TSA) is optional; offline signing is supported. Add TSA only if your policy requires it.

---

## Troubleshooting

- **`claim.malformed` / `ClaimDecoding("dc:format")`** — add a valid IANA media type in the claim (`image/jpeg`, `application/pdf`). The library sets this automatically in `TC_C2PA_EmplaceManifest`.
- **`algorithm.unsupported` / `UnknownAlgorithm`** — ensure your claim has `"alg": "sha256"` (the library sets this).
- **`assertion.dataHash.mismatch`** — the hard‑binding exclusion length must exactly match the final embed size (the library’s iterative embed fixes this).

Validate with `c2patool` to diagnose structure and trust.

---

## Contributing

- Use **Conventional Commits** (e.g., `feat:`, `fix:`, `style(ruff):`, `ci:`).  
- Run `ruff format` + `ruff check --fix` before committing.  
- Add unit tests for new behavior.

---

## License

MIT
