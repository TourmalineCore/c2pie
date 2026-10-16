## First steps

To contribute to the c2pie package development, you can use one of the following approaches **<u>after cloning the repository</u>**.

### General principles

🔸 Use Conventional Commits (e.g., `feat:`, `fix:`, `style(ruff):`, `ci:`).  

🔸 Run `Lint and Format` task before committing.  

🔸 Add unit tests for new behavior.

### Using Dev Containers
1. Make sure you have installed Docker and [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) extension for VS code.

2. Open the repo in VS Code and Reopen in Container. The container installs Python, Poetry, the package in editable mode, and configures Ruff as a default formatter, which provides linting and formatting and enables auto-fixing files on save (see `.devcontainer/devcontainer.json`).

### Automatic secrets detection

We have a pre-commit hook configured to run [gitleaks](https://github.com/gitleaks/gitleaks)-based secrets detection on commit to prevent vulnerable data from being committed. 

Pre-commit is also included in the dev dependency group for the project, so you'll be able to work with it once you activate Poetry's virtual environment.

>[!WARNING]
>Using pre-commit hook requires you to have Python installed locally. You can then install it either with Poetry or using `pip install pre-commit` even if you don't have Poetry locally, however, **Python is necessary**.
>
>Having this pre-commit hook isn't crucial at this point since we have additional secrets detection performed in CI on every push. If any secrets get to the repo, we'll immediately notice and will be able to remove them and change the credentials. Hence, as of now, we haven't made pre-commit check independent from a Python environment.

After installing the package, for the hook to work you need to run the following command in the environment you perform your commits to this repo from (with pre-commit package installed):
```
pre-commit install
``` 
> For Poetry environments: if the command doesn't work, try `poetry run pre-commit install` 

Meaning, if you're using a Git client for committing (i.e. not CLI), for this command to work you'll need to install this hook **in the local folder of this project**, not inside the container.

#### Secret detection in CI

As noted previously, Secrets Detection workflow using gitleaks is meant as an alarm system, not a one-in-all solution that competely prevents secrets from getting to the remote repository. 

If this workflow fails due to a real secret being detected, it's essential to follow these steps.

1.  **! Regenerate the secret**. The one that's been detected is already in the repo, so it can be considered leaked.

2. Remove the secret from the codebase. If it was in a file that needed to be git ignored, make sure that **_only after_** you add that file to .gitignore, you use the **_newly regenerated_** secret in the file.
   
3. Once the secret was dealt with, go to the logs of the failed Secrets Detection workflow run and extract the fingerprint of the detected secret. The logs are divided into separate blocks for each "finding" (detected secret). The fingerprint will be right above the last line in that block. It will have this format: `commit_hash:file_path:rule_id:line_number`, you can see actual examples in `.gitleaksignore`. Copy this fingerprint. Note that you might have multiple fingerprints from different commits referring to the same line and you need to get them all.
   
4. Add the copied fingerprint(-s) to `.gitleaksignore` in the repository's root directory. 
   
5. Now, after you commit `.gitleaksignore`, the workflow won't detect this secret in the repository's history. 

Gitleaks is currently configured in `.gitleaks.toml` to ignore mock credentials for tests and example app. However, if for some reason you added a new mock secret in a different location, add this location to `allowlists` section of `.gitleaks.toml`. If you forget to do that before commiting the mock secret, ignore the detected secret by adding its fingerprint to `.gitleaksignore` as described above. 

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