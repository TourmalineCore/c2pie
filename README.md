# TC-C2PA-PY
It is the open-source Python library which provide functionality of generation Content Credentials Manifest according to the [C2PA standard](https://c2pa.org/).   
Main goal is to help construct C2PA manifest, however it is crucial for the library user to know what the manifest should look like in the final state in order to use the library's methods correctly. 

Library usage example is located by following path: `test_application/test_app.py`.

## How to start this project

It is recommended to work with existing modules using [Dev containers](https://code.visualstudio.com/docs/devcontainers/containers) in Visual Studio Code.

### Prerequisites

- Install [WSL](https://ubuntu.com/desktop/wsl) 
- Install the Docker client ([Windows](https://docs.docker.com/desktop/setup/install/windows-install/) / [Mac](https://docs.docker.com/desktop/setup/install/mac-install/) / [Linux](https://docs.docker.com/desktop/setup/install/linux-install/)) 
  - Make sure Docker client is the latest version
  - Make sure Docker uses WSL 2 based engine

### Open the project

- Make sure Docker daemon is running before opening the dev container (`Ctrl + Shift + P` -> "Reopen in container" or click the button in the lower left corner -> "Reopen in container")
- Microsoft VS Code
  - VS Code should also have the "Dev Containers" extension installed. To check it, open "View: Extensions" with `Ctrl + Shift + X`.


### How to run project

There are VSCode tasks provided to interact with code. Please use `Ctrl + Shift + B` to open the context menu:
- `Run unit tests` task runs all unit tests that provided in `tests` folder.
- `Run test application` task runs the usage example of library that provided in `test_application` folder.
- `Build package` task builds the Python library package that configured in `setup.py` file.
