<picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TourmalineCore/c2pie/refs/heads/master/docs/images/c2pie-logo-for-dark-mode.svg"> 
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/TourmalineCore/c2pie/refs/heads/master/docs/images/c2pie-logo-for-light-mode.svg">
    <img xsalt="с2pie Logo" src="https://raw.githubusercontent.com/TourmalineCore/c2pie/refs/heads/master/docs/images/c2pie-logo-for-light-mode.svg" style="width: 50%;">
</picture>

-------

[![Linting and Testing](https://github.com/TourmalineCore/c2pie/actions/workflows/lint-and-test.yml/badge.svg?branch=develop)](https://github.com/TourmalineCore/c2pie/actions/workflows/lint-and-test.yml)
[![c2pa](https://img.shields.io/badge/c2pa-v1.4-seagreen.svg)](https://c2pa.org/)
[![coverage](https://img.shields.io/badge/coverage-87%25-olivedrab?logo=codecov&logoColor=ff9d1c)](https://github.com/TourmalineCore/c2pie/actions/workflows/lint-and-test.yml)
[![latest](https://img.shields.io/pypi/v/c2pie?label=latest&colorB=fc8021)](https://pypi.org/project/c2pie/)

<br>

`c2pie` is an open‑source Python library for constructing [C2PA](https://c2pa.org/) Content Credentials manifests that validate with [`c2patool`](https://github.com/contentauth/c2pa-rs) and other common C2PA consumers.

As far as we know, c2pie is **the world's first Python package** to implement signing PDF files according to the C2PA Standard.

The package supports building claims, assertions, and COSE signatures and embedding the manifest store into JPG/JPEG and PDF files.

🔸 **Supported file extensions**: `JPG`, `JPEG`, `PDF`

🔸 **Supported Python versions**: `3.9.2 - 3.14.0`

🔸 **Supported C2PA Spec Versions**: `1.4`. 

Support for C2PA 2.2 is planned for future releases.

For more detailed feature specification, please look at the [Features](#-features) section.


> [!WARNING]
> This library helps you build valid manifests, but trust decisions (anchors, allow/deny lists, TSA) are your responsibility. For production, you must provide a certificate chain anchored to an accepted trust root and configure validation policy accordingly. 
> 
> For more information on generating certificates and keys for file signing proceed to the [Certificates](#-certificates) section.

## Table of Contents
+ [🥧 Quick start](#-quick-start)
  + [Running signing from a Docker container](#running-signing-from-a-docker-container)
  + [Running from your local environment using globally installed Python](#running-from-your-local-environment-using-globally-installed-python)
    + [Prerequisites](#prerequisites)
    + [Usage](#usage)
      + [Command Line Interface](#command-line-interface)
      + [Code](#code)
  + [Running example apps with Docker Compose](#running-example-apps-with-docker-compose)
  + [Validation](#validation)
    + [C2PA Verify Tool](#c2pa-verify-tool)
    + [c2patool](#c2patool)
      + [Validating test image with a Docker container](#validating-test-image-with-a-docker-container)
+ [🥧 Certificates](#-certificates)
  + [Generating test credentials](#generating-test-credentials)
  + [Getting credentials for production](#getting-credentials-for-production)
+ [🥧 Features](#-features)
  + [Workflow of test applications](#workflow-of-test-applications)
  + [Notes for PDF vs JPG/JPEG](#notes-for-pdf-vs-jpgjpeg)
+ [🥧 Relevant links](#-relevant-links)
+ [🥧 License](#-license)

<br>

# 🥧 Quick start

## Running signing from a Docker container

1) Run a Docker container from a Python image:
```bash
docker run --rm -it --entrypoint bash --name c2pie-test python:3.14
```

2) Inside the container execute the following bash commands:

```bash
# Generate private key and certificate chain:
openssl genpkey \
-algorithm RSA-PSS \
-pkeyopt rsa_keygen_bits:2048 \
-pkeyopt rsa_pss_keygen_md:sha256 \
-pkeyopt rsa_pss_keygen_mgf1_md:sha256 \
-pkeyopt rsa_pss_keygen_saltlen:32 \
-out private_key.key

openssl req -new -x509 \
-key private_key.key \
-sha256 -days 365 \
-subj "/C=US/ST=CA/L=Somewhere/O=C2PA Test Signing Cert/OU=FOR TESTING_ONLY/CN=C2PA PSS Signer/emailAddress=pie@example.com" \
-addext "basicConstraints=critical,CA:false" \
-addext "keyUsage=critical,digitalSignature,nonRepudiation" \
-addext "extendedKeyUsage=critical,emailProtection" \
-out certificate_chain.pem

# Export created private key and certificate chain files into env variables:
export C2PIE_PRIVATE_KEY_FILE=./private_key.key
export C2PIE_CERTIFICATE_CHAIN_FILE=./certificate_chain.pem

# Install package
pip install c2pie 

# Download test image from this repo
wget https://raw.githubusercontent.com/TourmalineCore/c2pie/refs/heads/master/example_app/test_files/test_image.jpg

# Sign downloaded image
c2pie sign --input_file ./test_image.jpg
```

3) **In a separate terminal**, execute the following commands to copy the file from the container to the folder you're currently in:

```bash
docker cp c2pie-test:signed_test_image.jpg .
```

>[!NOTE]
>You can use the `c2pie-test` container to experiment with other JPG/JPEG or PDF files.
>
>Once you exit the container, it will be deleted automatically.

After being copied to host machine, signed files can then be validated using either of the methods from [Validation](#validation) section: [C2PA Verify Tool](https://contentcredentials.org/verify) or [c2patool](#validating-test-image-with-a-docker-container).

<br>

## Running from your local environment using globally installed Python

### Prerequisites

1) Python environment. Currently supported Python versions: 3.9.2 - 3.14.0. Make sure to [create and activate virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) to avoid installing packages globally and any errors caused by that.

2) Private key and certificate chain pair. The repo contains pre-generated mock credentials in `tests/credentials`. You can either download and use them for a quick start or go to [Certificates](#-certificates) for instructions on how to generate a similar key-certificate pair.


3) Key and certificate chain filepaths exported into the current environment with (pay attention to filenames):
    ```bash
    export C2PIE_PRIVATE_KEY_FILE=private_key.key
    export C2PIE_CERTIFICATE_CHAIN_FILE=certificate_chain.pem
    ```

4) c2pie package installed in your current environment:

    ```bash
    pip install c2pie
    ```

### Usage

#### Command Line Interface

You can run the following command to sign an input JPG or PDF file:
```python
c2pie sign --input_file path/to/input_file
```

By default, signed file will be saved to the same directory as the input file with the *signed_* prefix. 
To explicitly set output path, use:
```python
c2pie sign --input_file path/to/input_file --output_file path/to/output_file
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

<br>

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

## Validation

### C2PA Verify Tool

You can verify signed files using [Verify tool](https://contentcredentials.org/verify).

Simply upload the file you'd like to verify.

>[!IMPORTANT]
> Files embedded with self-signed certificates (like the ones this repository contains) **won't be verified**. 
> 
> You'll get the following message:
>```
>The Content Credential issuer couldn’t be recognized. This file may not come from where it claims to.
>```
>
>Please proceed to [production credentials section](#getting-credentials-for-production) to find out about generating verifiable credentials.

### c2patool 

[c2patool](https://github.com/contentauth/c2pa-rs/tree/main/cli) is a command line tool for working with C2PA manifests and media assets (audio, image or video files) provided by the C2PA Rust Library.

If you already have Rust, install c2patool with:
```bash
cargo install c2patool
```

To validate files with c2patool, run:
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

#### Validating test image with a Docker container

1. Run a container with Rust:
```bash
docker run --rm -it --entrypoint bash --name c2pie-validate rust:1.90.0-bullseye
```

2. Install c2patool in the container:
```bash
cargo install c2patool
```

3. To validate the image [previously signed using a Docker container](#running-signing-from-a-docker-container) and copied to your working directory:
   
   **In a separate terminal**, copy the signed image into the Rust container. 
   > Make sure the signed file is in the same directory that you're running this `docker cp` from!
    ```bash
    docker cp ./signed_test_image.jpg c2pie-validate:signed_test_image.jpg
    ```
    Then **go back to the container's terminal** and validate the copied image with:
    ```bash
    c2patool signed_test_image.jpg
    ```

    If the validation was successful, you'll get an output similar to this:
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

>[!NOTE]
>You can validate other files in the same `c2pie-validate` container. 
>
>Once you exit, the container will be deleted automatically.

<br>

# 🥧 Certificates

Example certificate chain and key file are located in `tests/credentials`. 

>[!WARNING]
>This repository's credentials are suitable for development only! 

## Generating test credentials

You can generate your own private key and certificate chain pair for testing the package by following these steps:

1. Generate a private key:
    ```bash
    openssl genpkey \
    -algorithm RSA-PSS \
    -pkeyopt rsa_keygen_bits:2048 \
    -pkeyopt rsa_pss_keygen_md:sha256 \
    -pkeyopt rsa_pss_keygen_mgf1_md:sha256 \
    -pkeyopt rsa_pss_keygen_saltlen:32 \
    -out private_key.key
    ```

2. Generate a Self-Signed Certificate:
    ```bash
    openssl req -new -x509 \
    -key private_key.key \
    -sha256 -days 365 \
    -subj "/C=US/ST=CA/L=Somewhere/O=C2PA Test Signing Cert/OU=FOR TESTING_ONLY/CN=C2PA PSS Signer/emailAddress=pie@example.com" \
    -addext "basicConstraints=critical,CA:false" \
    -addext "keyUsage=critical,digitalSignature,nonRepudiation" \
    -addext "extendedKeyUsage=critical,emailProtection" \
    -out certificate_chain.pem
    ```

>[!IMPORTANT]
> Remember to update environment variables `C2PIE_PRIVATE_KEY_FILE` and `C2PIE_CERTIFICATE_CHAIN_FILE` to use your newly generated key (`private_key.key`) and certificate chain (`certificate_chain.pem`) files.

>[!NOTE]
> You can change certificate's validity period with `-days` option at the last step.
>
> `-subj` option allows to set signature info used to sign the certificate. You can change the values to fit your info. Here's what each field letter code stands for:
> 
> **/C** - Counry Code, **/ST** - State or Province name, **/L** - Locality Name (e.g. city), **/O** - Organization Name, **/OU** - Organization Unit Name, **/CN** - Common Name (e.g. your name), **/emailAdress** - email adress


## Getting credentials for production

🔸 Use a real document‑signing certificate (RSA‑PSS or ECDSA per C2PA);

🔸 Provide a leaf + intermediates bundle (no root);  

🔸 Configure trust anchors/allow‑lists in your validator environment. 

For detailed information on signing and certificates please explore the [corresponding section in the Content Authenticity Initiative (CAI) documentation](https://opensource.contentauthenticity.org/docs/signing/).

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

# 🥧 Relevant links
∗ [CAI documentation](https://opensource.contentauthenticity.org/docs)

∗ [C2PA spec](https://c2pa.org/)  

∗ [c2patool for validation](https://github.com/contentauth/c2pa-rs)

∗ [C2PA Verify Tool](https://contentcredentials.org/verify)

<br>

# 🥧 License

Apache License. See [c2pie repository's license](LICENSE) for more information.

