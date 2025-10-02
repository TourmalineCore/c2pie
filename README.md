<picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/c2pie-logo-for-dark-mode.svg"> 
    <source media="(prefers-color-scheme: light)" srcset="docs/images/c2pie-logo-for-light-mode.svg">
    <img xsalt="с2pie Logo" src="docs/images/c2pie-logo-for-light-mode.svg" style="width: 50%;">
</picture>

-------

[![Unit Tests](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/run_unit_tests.yml/badge.svg)](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/run_unit_tests.yml)
[![Lint](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/lint.yml/badge.svg)](https://github.com/TourmalineCore/tc-c2pa-py/actions/workflows/lint.yml)

<br>

**c2pie** is an open‑source Python library for constructing [C2PA](https://c2pa.org/) Content Credentials manifests that validate with [`c2patool`](https://github.com/contentauth/c2pa-rs) and other common C2PA consumers. 

The package supports building claims, assertions, and COSE signatures and embedding the manifest store into JPEG and PDF files. 

For more detailed feature specification, please look at the [Features](#-features) section.

> ⚠️ This library helps you build valid manifests, but trust decisions (anchors, allow/deny lists, TSA) are your responsibility. For production, you must provide a certificate chain anchored to an accepted trust root and configure validation policy accordingly.

## Table of Content
+ [🥧 Quick start](#-quick-start)
  + [Prerequisites](#prerequisites)
  + [Usage](#usage)
    + [Command Line Interface](#command-line-interface)
    + [Code](#code)
    + [Validation](#validation)
+ [🥧 For developers](#-for-developers)
  + [Run test applications](#run-test-applications)
  + [Run tests](#run-tests)
  + [Lint \& format](#lint--format)
  + [CI](#ci)
+ [🥧 Features](#-features)
  + [Workflow of test applications](#workflow-of-test-applications)
  + [Notes for PDF vs JPEG](#notes-for-pdf-vs-jpeg)
+ [🥧 Certificates](#-certificates)
  + [Generating your own mock credentials](#generating-your-own-mock-credentials)
  + [Getting credentials for production](#getting-credentials-for-production)
+ [🥧 Relevant links](#-relevant-links)
+ [🥧 Contributing](#-contributing)
+ [🥧 License](#-license)

<br>

# 🥧 Quick start


## Prerequisites

1) Python environment. Currently supported Python versions: 3.9 - 3.13
2) Private key and certificate chain pair. 
3) Key and certificate filepaths exported into the current environment with:
    ```bash
    export C2PIE_KEY_FILEPATH=path/to/your/private/key/file
    export C2PIE_CERT_FILEPATH=path/to/your/certificate/chain/file
    ```
4) Install c2pie package by running this command from the current environment:

    ```bash
    pip install c2pie
    ```


## Usage


### Command Line Interface

You can run the following command to sign an input JPG/JPEG or PDF file:
```python
c2pie sign --input_file path/to/input_file
```

By default, signed file will be saved to the same directory as the input file with the *signed_* prefix. 
To explicitly set output path, use:
```python
c2pie sign --input_file path/to/input_file --output_file path/to/output/file
```

### Code

To sign a file and save the output to the same directory:

```python
from c2pie.signing import sign_file

input_file_path = "path/to/file"
sign_file(input_path=input_file_path)
```

To set a custom output path:
```python
from c2pie.signing import sign_file

input_file_path = "path/to/file"
output_file_path = "path/to/another/file/"
sign_file(input_path=input_file_path, output_path=output_file_path)
```

### Validation


Output files can be validated with:
```bash
c2patool path/to/your_output.jpg
c2patool path/to/your_output.pdf
```

<br>

# 🥧 For developers

First of all, clone and (optionally) use [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers):

1. (optional) Install Docker and VS Code “Dev Containers” extension.  

2. Open the repo in VS Code and Reopen in Container. The container installs Python, your package in editable mode, and configures Ruff which provided linting and formatting on save.

> Dev container also sets Ruff as default formatter and enables auto-fixing on save (see `.devcontainer/devcontainer.json`).


## Run test applications

To run test applications, you need to fill out `TEST_PDF_PATH` and/or `TEST_IMAGE_PATH` in values in *.env*. Test scripts use these filepaths as input files for signing.

Also make sure that you have test certificate chain and public key in `tests/credentials`. They should be there by default if you've cloned the repository. If needed, you can change their filepaths in *.env* as well.

>We recommend using Dev Containers here in order to automatically create an environment with all dependencies installed and environment variables exported.


You can test the signing workflow with the following VS Code tasks:

🔸 `Run JPEG test application` 

🔸 `Run PDF test application`

## Run tests

Run from terminal:
```python
pytest
```

Or use the VC Code task `Run unit tests`. Note that the task excludes the e2e test. 

Or if you'd like to get info on test coverage, use:
```python
pytest --cov
```

## Lint & format

You can check if there are any issues to deal with them manually:

```python
ruff format --check .
ruff check .
```

Or check and automatically fix where possible:
```python
ruff format .
ruff check . --fix
```

The latter option is also available via the VC Code task `Lint and Format`

## CI

#TODO

<br>

# 🥧 Features

🔸 C2PA Claim (`c2pa.claim`) with canonical CBOR, `dc:format`, `alg`, and hashed‑URIs for assertions.

🔸 C2PA Signature (`c2pa.signature`) using COSE_Sign1 (PS256) with detached payload and `x5chain` in protected header.

🔸 Assertion Store with common assertions (e.g., `c2pa.hash.data` hard‑binding, schema.org CreativeWork, etc.).

🔸 Embedding
  - JPEG via APP11 segments (size‑driven iterative layout).
  - PDF via incremental update at EOF (xref/trailer preserved; `/AF` + `/Names/EmbeddedFiles`).  

🔸 Validation with `c2patool` (structure + signatures).

## Workflow of test applications

1) Load a sample asset (`tests/test_files/..`);

2) Build a manifest with `c2pie_GenerateAssertion`, `c2pie_GenerateHashDataAssertion`, `c2pie_GenerateManifest` 

3) Embed the manifest (`c2pie_EmplaceManifest`);  

4) Write a new asset with C2PA.

## Notes for PDF vs JPEG

🔸 **PDF**: we append an incremental update. The `c2pa.hash.data` exclusion starts at `len(original_pdf)` and its length equals the final tail size (computed iteratively).  

🔸 **JPEG**: we insert APP11 segments. The exclusion start is the APP11 insertion offset; the length is the final APP11 payload length (also computed iteratively).

The library takes care of iterative sizing so the `c2pa.hash.data` matches exactly, otherwise validators return `assertion.dataHash.mismatch`.

<br>

# 🥧 Certificates

Example certificate and key are located in `tests/credentials`. They are suitable for development only ⚠️

## Generating your own mock credentials

You can generate your own mock credentials for testing and developing the package follow these steps:

1. Generate a private key:
    ```bash
    openssl genrsa -out credentials/<private-key-filename>.pem 2048
    ```

2. Generate a Certificate Signing Request (CSR):
    ```bash
    openssl req -new \
    -key credentials/<private-key-filename>.pem \
    -out csr.pem
    ```

3. Generate a Self-Signed Certificate:
    ```bash
    openssl x509 -req -days 365 \
    -in csr.pem \
    -signkey  credentials/<private-key-filename>.pem \
    -out credentials/<certificate-filename>.pem
    ```
> ⚠️ Remember to update environment variables to use your newly generated credentials.

> You can change certificate's validity period with --days option at the last step.

> Certificate Signing Request file (*csr.pem*) can be deleted after the certificate has been generated.


## Getting credentials for production

🔸 Use a real document‑signing certificate (RSA‑PSS or ECDSA per C2PA);

🔸 Provide a leaf + intermediates bundle (no root);  

🔸 Configure trust anchors/allow‑lists in your validator environment. 

For detailed information on signing and certificates please explore the [corresponding section in the Content Authenticity Initiative (CAI) documentation](https://opensource.contentauthenticity.org/docs/signing/).

<br>

# 🥧 Relevant links
∗ [CAI documentation](https://opensource.contentauthenticity.org/docs)

∗ [C2PA spec](https://c2pa.org/)  

∗ [c2patool for validation](https://github.com/contentauth/c2pa-rs)

<br>

# 🥧 Contributing

🔸 Use Conventional Commits (e.g., `feat:`, `fix:`, `style(ruff):`, `ci:`).  

🔸 Run `Lint and Format` task before committing.  

🔸 Add unit tests for new behavior.

<br>

# 🥧 License

Apache License. See [c2pie repository's license](LICENSE) for more information.

