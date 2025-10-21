<picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TourmalineCore/c2pie/refs/heads/master/docs/images/c2pie-logo-for-dark-mode.svg"> 
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/TourmalineCore/c2pie/refs/heads/master/docs/images/c2pie-logo-for-light-mode.svg">
    <img xsalt="с2pie Logo" src="https://raw.githubusercontent.com/TourmalineCore/c2pie/refs/heads/master/docs/images/c2pie-logo-for-light-mode.svg" style="width: 50%;">
</picture>

-------

[![CI](https://github.com/TourmalineCore/c2pie/actions/workflows/lint-and-test.yml/badge.svg)](https://github.com/TourmalineCore/c2pie/actions/workflows/lint-and-test.yml)
[![c2pa](https://img.shields.io/badge/c2pa-v1.4-seagreen.svg)](https://c2pa.org/)
[![coverage](https://img.shields.io/badge/coverage-91%25-forestgreen?logo=codecov&logoColor=ff9d1c)](https://github.com/TourmalineCore/c2pie/actions/workflows/lint-and-test.yml)
[![latest](https://img.shields.io/pypi/v/c2pie?label=latest&colorB=fc8021)](https://pypi.org/project/c2pie/)

<br>

**c2pie** is an open‑source Python library for constructing [C2PA](https://c2pa.org/) Content Credentials manifests that validate with [`c2patool`](https://github.com/contentauth/c2pa-rs) and other common C2PA consumers. 

The package supports building claims, assertions, and COSE signatures and embedding the manifest store into JPG/JPEG and PDF files. 

🔸 **Supported file extensions**: `JPG`, `JPEG`, `PDF`

🔸 **Supported Python versions**: `3.9.2 - 3.14.0`

🔸 **C2PA Spec Version**: `1.4`

For more detailed feature specification, please look at the [Features](#-features) section.


> [!WARNING]
> This library helps you build valid manifests, but trust decisions (anchors, allow/deny lists, TSA) are your responsibility. For production, you must provide a certificate chain anchored to an accepted trust root and configure validation policy accordingly. 
> 
> For more information on generating certificates and keys for file signing proceed to the [Certificates](#-certificates) section.

## Table of Contents
+ [🥧 Quick start](#-quick-start)
  + [Running example apps with Docker Compose](#running-example-apps-with-docker-compose)
  + [Running from your own environment](#running-from-your-own-environment)
    + [Prerequisites](#prerequisites)
    + [Usage](#usage)
      + [Command Line Interface](#command-line-interface)
      + [Code](#code)
    + [Validation](#validation)
      + [c2patool](#c2patool)
      + [C2PA Verify Tool](#c2pa-verify-tool)
+ [🥧 For developers](#-for-developers)
  + [First steps](#first-steps)
    + [Using Dev Containers](#using-dev-containers)
    + [Using a Local Environment](#using-a-local-environment)
  + [Run test applications](#run-test-applications)
  + [Run tests](#run-tests)
  + [Lint \& format](#lint--format)
+ [🥧 Features](#-features)
  + [Workflow of test applications](#workflow-of-test-applications)
  + [Notes for PDF vs JPG/JPEG](#notes-for-pdf-vs-jpgjpeg)
+ [🥧 Certificates](#-certificates)
  + [Generating your own mock credentials](#generating-your-own-mock-credentials)
  + [Getting credentials for production](#getting-credentials-for-production)
+ [🥧 Relevant links](#-relevant-links)
+ [🥧 Contributing](#-contributing)
+ [🥧 License](#-license)

<br>

# 🥧 Quick start

## Running example apps with Docker Compose

For a quick test of c2pie's functionality with pre-prepared environment, test files and credentials, you can run our example apps.

>[!IMPORTANT]
> Docker is essential for running example apps.

Follow the steps:

1. Clone the c2pie repository.

2. Go to `example_app` directory:
    ```bash
    cd example_app
    ```

>[!NOTE]
>By default, example apps use the latest available stable c2pie version. If you'd like to test some particular version, you can change the value of `C2PIE_PACKAGE_VERSION` in `example_app/.example-app-env`. 

3. To test signing a JPG file, run:
    ```bash
    docker compose up c2pie-test-signing-jpg
    ```
  
   To test signing a PDF file, run:
    ```bash
    docker compose up c2pie-test-signing-pdf
    ```

    After running either of these commands, you'll see a resulting signed file appear in `example_app/test_files` directory with a `signed-` prefix and a corresponding message with c2patool validation results in your terminal like this:
    
    ```bash
    Successfully signed the file test_files/test_image.jpg!
    The result was saved to test_files/signed_test_image.jpg. 
    c2patool_validation_results:
    {
        "active_manifest": "urn:uuid:f0ce8560b76342d1bb3085cfbe6cc5e9",
        "manifests": {
        "urn:uuid:f0ce8560b76342d1bb3085cfbe6cc5e9": {
            "claim_generator": "c2pie",
        ................
    },
    "validation_results": {
        "activeManifest": {
        "success": [
            {
                "code": "claimSignature.insideValidity",
                "url": "self#jumbf=/c2pa/urn:uuid:f0ce8560b76342d1bb3085cfbe6cc5e9/c2pa.signature",
                "explanation": "claim signature valid"
            },
        ................
        },
        "validation_state": "Valid" 
    }
    ```

You can also set up a Jupyter Lab environment and test c2pie there by running:
```bash
docker compose up c2pie-notebooks
```

After running this command you should be able to access Jupyter Lab at `localhost:8888` from your browser.

The existing `notebooks` directory already contains an example notebook with commands to test signing functionality. 

<br>

## Running from your own environment

### Prerequisites

1) Python environment. Currently supported Python versions: 3.9.2 - 3.14.0.
2) Private key and certificate chain pair. You can go to [Certificates](#-certificates) for instructions on how to generate one.

    The repo contains pre-generated mock credentials in `tests/credentials`. You can use them for a quick start.

3) Key and certificate filepaths exported into the current environment with:
    ```bash
    export C2PIE_KEY_FILEPATH=<path/to/private_key_file>
    export C2PIE_CERT_FILEPATH=<path/to/certificate_chain_file>
    ```

4) c2pie package installed in your current environment:

    ```bash
    pip install c2pie
    ```


### Usage

#### Command Line Interface

You can run the following command to sign an input JPG or PDF file:
```python
c2pie sign --input_file <path/to/input_file>
```

By default, signed file will be saved to the same directory as the input file with the *signed_* prefix. 
To explicitly set output path, use:
```python
c2pie sign --input_file <path/to/input_file> --output_file <path/to/output_file>
```

If the file has been successfully signed, you'll see a message like this: 
```bash
Successfully signed the file tests/test_files/test_doc.pdf!
The result was saved to tests/test_files/signed_test_doc.pdf.
```

#### Code

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

If the file has been successfully signed, you'll see a message like this: 
```bash
Successfully signed the file tests/test_files/test_doc.pdf!
The result was saved to tests/test_files/signed_test_doc.pdf.
```

### Validation

#### c2patool 

Output files can be validated with:
```bash
c2patool path/to/your_output.jpg
c2patool path/to/your_output.pdf
```

If the file has been correctly signed and validation is successful, the results you'll see in the terminal will look similar to this:
```bash
c2patool_validation_results:
{
    "active_manifest": "urn:uuid:f0ce8560b76342d1bb3085cfbe6cc5e9",
    "manifests": {
    "urn:uuid:f0ce8560b76342d1bb3085cfbe6cc5e9": {
        "claim_generator": "c2pie",
    ................
},
"validation_results": {
    "activeManifest": {
    "success": [
        {
            "code": "claimSignature.insideValidity",
            "url": "self#jumbf=/c2pa/urn:uuid:f0ce8560b76342d1bb3085cfbe6cc5e9/c2pa.signature",
            "explanation": "claim signature valid"
        },
    ................
    },
    "validation_state": "Valid" 
}
```

#### C2PA Verify Tool

You can also verify signed files using [Verify tool](https://contentcredentials.org/verify).

Simply upload the file you'd like to verify.

>[!IMPORTANT]
> Files embedded with self-signed certificates (like the ones this repository contains) **won't be verified**. 
> 
> You'll get the following message:
>```
>The Content Credential issuer couldn’t be recognized. This file may not come from where it claims to.
>```
>
>Please proceed to [production credentials section](#-getting-credentials-for-production) to find out about generating verifiable credentials.

<br>

# 🥧 For developers

## First steps

To contribute to the c2pie package development, you can use one of the following approaches **<u>after cloning the repository</u>**.

### Using Dev Containers
1. Make sure you have installed Docker and [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) extension for VS code.

2. Open the repo in VS Code and Reopen in Container. The container installs Python, Poetry, the package in editable mode, and configures Ruff as a default formatter, which provides linting and formatting and enables auto-fixing files on save (see `.devcontainer/devcontainer.json`).

### Using a Local Environment

>[!NOTE]
>We strongly recommend using Dev Containers in order to automatically create an isolated Python environment with all dependencies installed, environment variables exported and some helpful development tools included.


1. Make sure the environment you're currently in has Python and Poetry installed and their versions meet the requirements of the project. You can verify that by running:

    ```bash
    python --version
    poetry --version
    ```

2. Go to the repository's folder in terminal and run:
    ```bash
    poetry install
    ```
    This will automatically create and activate a poetry shell with project's dependencies installed.


3. To run any Python command related to the project's dependencies, remember to add `poetry run` in front of the command. For example:
    ```bash
    poetry run c2pie sign --input_file tests/test_files/test_doc.pdf
    
    poetry run ruff check
    ```
>[!WARNING]
> Commands in further sections don't include `poetry run` by default as they are intended to be run from a Dev Container. Remember to add `poetry run`.


## Run test applications

To run test applications, you need to fill out `TEST_PDF_PATH` and/or `TEST_IMAGE_PATH` in values in *.env*. Test scripts use these filepaths as input files for signing.

Also make sure that you have test certificate chain and public key in `tests/credentials`. They should be there by default if you've cloned the repository. If needed, you can change their filepaths in *.env* as well.


You can test the signing workflow with the following VS Code tasks:

🔸 `Run JPG test application` 

🔸 `Run PDF test application`

## Run tests

Run from terminal:
```bash
pytest
```

Or use the VC Code task `Run unit tests`. Note that the task excludes the e2e test. 

Or if you'd like to get info on test coverage, use:
```bash
pytest --cov
```

## Lint & format

You can check if there are any issues to deal with them manually:

```bash
ruff format --check .
ruff check .
```

Or check and automatically fix where possible:
```bash
ruff format .
ruff check . --fix
```

The latter option is also available via the VC Code task `Lint and Format`

<br>

# 🥧 Features

🔸 C2PA Claim (`c2pa.claim`) with canonical CBOR, `dc:format`, `alg`, and hashed‑URIs for assertions.

🔸 C2PA Signature (`c2pa.signature`) using COSE_Sign1 (PS256) with detached payload and `x5chain` in protected header.

🔸 Assertion Store with common assertions (e.g., `c2pa.hash.data` hard‑binding, schema.org CreativeWork, etc.).

🔸 Embedding
  - JPG via APP11 segments (size‑driven iterative layout).
  - PDF via incremental update at EOF (xref/trailer preserved; `/AF` + `/Names/EmbeddedFiles`).  

🔸 Validation with `c2patool` (structure + signatures).

## Workflow of test applications

1) Load a sample asset (`tests/test_files/..`);

2) Build a manifest with `c2pie_GenerateAssertion`, `c2pie_GenerateHashDataAssertion`, `c2pie_GenerateManifest`;

3) Embed the manifest (`c2pie_EmplaceManifest`);  

4) Write a new asset with C2PA.

## Notes for PDF vs JPG/JPEG

🔸 **PDF**: we append an incremental update. The `c2pa.hash.data` exclusion starts at `len(original_pdf)` and its length equals the final tail size (computed iteratively).  

🔸 **JPG/JPEG**: we insert APP11 segments. The exclusion start is the APP11 insertion offset; the length is the final APP11 payload length (also computed iteratively).

The library takes care of iterative sizing, so the `c2pa.hash.data` matches exactly, otherwise validators return `assertion.dataHash.mismatch`.

<br>

# 🥧 Certificates

Example certificate and key are located in `tests/credentials`. 

>[!WARNING]
>This repository's credentials are suitable for development only! 

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
>[!IMPORTANT]
> Remember to update environment variables to use your newly generated credentials.

>[!NOTE]
> You can change certificate's validity period with --days option at the last step.
>
>Certificate Signing Request file (*csr.pem*) can be deleted after the certificate has been generated.


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

∗ [C2PA Verify Tool](https://contentcredentials.org/verify)

<br>

# 🥧 Contributing

🔸 Use Conventional Commits (e.g., `feat:`, `fix:`, `style(ruff):`, `ci:`).  

🔸 Run `Lint and Format` task before committing.  

🔸 Add unit tests for new behavior.

<br>

# 🥧 License

Apache License. See [c2pie repository's license](LICENSE) for more information.

