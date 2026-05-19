## First steps

To contribute to the c2pie package development, you can use one of the following approaches **<u>after cloning the repository</u>**.

### General principles

🔸 Use Conventional Commits (e.g., `feat:`, `fix:`, `style(ruff):`, `ci:`). 

🔸 Use [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) branches names (e.g., `feature/`, `fix/`, `release/`).  

🔸 Run `Lint and Format` task before committing.  

🔸 Add unit tests for new behavior.

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

## Release Process

Releases are fully automated via [semantic-release](https://semantic-release.gitbook.io/). No manual version bumping or tagging is needed.

### Release triggers

A release is created automatically on push to `master`, `release/*`, or `develop` if there are commits with a release-triggering type (`feat`, `fix`, `docs`, `refactor`) since the last release.

### Version tags

```
develop        →  1.4.0-alpha.1, 1.4.0-alpha.2, ...
release/1.4.0  →  1.4.0-rc.1, 1.4.0-rc.2, ...
master         →  1.4.0
```

### Preparing a release

1. Create a `release/X.Y.0` branch from `develop`.

2. Only bug fixes and release-related commits are made on this branch. Each push generates a new RC: `1.4.0-rc.1`, `1.4.0-rc.2`, etc.

3. When the release is ready, merge into `master` via PR. The stable release `1.4.0` is created automatically on merge.

### Preparing a alpha release 

1. Create a `feature/*` or `fix/*` branch from `develop`.
> Note: naming of branch will be with number of issue and name of issue (e.g. `feature/#67-add-feature`).

2. Make the changes.

3. When changes are made, merge into `develop`. The alpha release `1.4.0-alpha.1` is created automatically on merge.

### Version bump

| Commit type | Bump | Example |
|---|---|---|
| `fix` | patch | `1.4.0 → 1.4.1` |
| `feat` | minor | `1.4.0 → 1.5.0` |
| `feat!` / `BREAKING CHANGE` | major | `1.4.0 → 2.0.0` |

### Backmerge

After every release on `master` or `release/*`, semantic-release automatically merges the release commit back into `develop`. This keeps `develop` in sync with the latest released version and ensures that the release commit (with updated `CHANGELOG.md` and `pyproject.toml`) is not lost.

| Release on | Merged back into |
|---|---|
| `master` | `develop` |
| `release/*` | `develop` |

> Note: Backmerged commit to the `develop` branch has the `[skip ci]` tag, so a new alpha release from the `develop` branch will not be created.