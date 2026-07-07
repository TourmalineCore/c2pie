# Releases scenario

## Initializing the repository

- Create a new repository with a default `master` branch
- Create a commit `Initial commit` (hash `abc1`):
    - (Added) .gitattributes
    - (Added) README.md
- Pushing the `Initial commit` (hash `abc1`) to the `master` branch
- Creating the `develop` branch from the `Initial commit` (hash `abc1`)

## Adding the Semantic Release Workflow

- 🌿 Create the branch `feature/#1-add-semantic-release-workflow` (later `feature/#1-**`) from the `Initial commit` (hash `abc1`) on the `develop` branch
- 📝 Create the commit `ci: #1: add semantic release workflow` (hash `abc2`):
    - (Added) github/workflows/.reusable-semantic-release-workflow.yml
- ➡️ Push the commit `ci: #1: add semantic release workflow` (hash `abc2`) to the `feature/#1-**` branch:
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 The `.reusable-semantic-release-workflow` workflow runs on the `feature/#1-**` branch; a **feature** release with the tag `1.0.0-sha-abc2` is expected
    - Commit `abc2` is tagged with `1.0.0-sha-abc2`
    - The `1.0.0-sha-abc2` release has appeared in GitHub Releases
    - The `1.0.0-sha-abc2` release has been published on PyPI

<!-- [?] It seems that it's not possible to start with version `0.1.0-sha-abc2` in a semantic release, so we'll start with `1.0.0-sha-abc2` -->

- 🔗 Create PR (#1):
    - Commit message `ci: #1: add semantic release workflow` 
    - `feature/#1-**` -> `develop`
    - Squash merge

- Merge the commit `ci: #1: add semantic release workflow (#1)` (hash `abc3`) into `develop`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Run the `.reusable-semantic-release-workflow` workflow on the `develop` branch; It is expected that the new release will **not** be published

## Adding a Test Execution Workflow

- 🌿 Create a branch named `feature/#2-add-test-execution-workflow` (later `feature/#2-**`) from the commit `ci: #1: add semantic release workflow (#1)` (hash `abc3`) on the `develop` branch
- 📝 Create the commit `ci: #2: add test execution workflow` (hash `abc4`):
    - (Added) github/workflows/test-execution-workflow.yml
- ➡️ Push the commit `ci: #2: add test execution workflow` (hash `abc4`) to the `feature/#2-**` branch:
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 The `.reusable-semantic-release-workflow` workflow runs on the `feature/#2-**` branch; a **feature** release with the tag `1.0.0-sha-abc4` is expected
    - Commit `abc4` is tagged with `1.0.0-sha-abc4`
    - The `1.0.0-sha-abc4` release has appeared in GitHub Releases
    - The `1.0.0-sha-abc4` release has been published on PyPI

- 🤖 Run the `test-execution-workflow` workflow on the `feature/#2-**` branch
    - All tests passed (0 tests found)

- 🔗 Create PR (#2):
    - Commit message `ci: #2: add test execution workflow` 
    - `feature/#2-**` -> `develop`
    - Squash merge

- Merge the commit `ci: #2: add test execution workflow (#2)` (hash `abc5`) into `develop`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Run the `.reusable-semantic-release-workflow` workflow on the `develop` branch; It is expected that the new release will **not** be published

- 🤖 Run the `test-execution-workflow` workflow on the `feature/#2-**` branch
    - All tests passed (0 tests found)

## Adding new functionality (in parallel with `feature/#2-**`)

- 🌿 Create the `feature/#3-add-read-logic` branch (later `feature/#3-**`) from the `ci: #2: add semantic release workflow (#1)` commit (hash `abc3`) on the `develop` branch
- 📝 Create a commit `test: #3: add a test to verify the logic for reading data from the console` (hash `abc6`):
    ```python
    function test_logic_for_reading_a_number_from_the_console():
        catch_call read_from_console() return 5:
            result = read_number_from_console_and_return_it()

        check result = 5
    ```
- ➡️ Push the commit `test: #3: add a test to verify the logic for reading data from the console` (hash `abc6`) to the `feature/#3-**` branch:
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 The `.reusable-semantic-release-workflow` workflow is triggered on the `feature/#3-**` branch; a **feature** release with the tag `1.0.0-sha-abc6` is expected
    - Commit `abc6` is tagged with `1.0.0-sha-abc6`
    - The `1.0.0-sha-abc6` release has appeared in GitHub Releases
    - The `1.0.0-sha-abc6` release has been published on PyPI

- 📝 Creating the commit `feat: #3: add read logic with printing` (hash `abc7`):
    ```python
    function read_number_from_console_and_return_it():
        number = read_from_console()
        return number

    function main():
        number = read_number_from_console_and_return_it()
        print(number)

        return 0
    ```
- ➡️ Push the commit `feat: #3: add read logic with printing` (hash `abc7`) to the `feature/#3-**` branch:
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 The `.reusable-semantic-release-workflow` workflow is triggered on the `feature/#3-**` branch; a **feature** release with the tag `1.0.0-sha-abc7` is expected
    - Commit `abc7` is tagged with `1.0.0-sha-abc7`
    - The `1.0.0-sha-abc7` release has appeared in GitHub Releases
    - The `1.0.0-sha-abc7` release has been published on PyPI

- 🔗 Create PR (#3):
    - Commit message `feat: #3: add read logic with printing`
    - `feature/#3-**` -> `develop`
    - Squash merge

- Merged commit `feat: #3: add read logic with printing (#3)` (hash `abc8`) into `develop`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Run the `.reusable-semantic-release-workflow` workflow on the `develop` branch; an **alpha** release with the tag `1.0.0-alpha.1` is expected
    - Commit `abc8` is tagged with `1.0.0-alpha.1`
    - The `1.0.0-alpha.1` release has appeared in GitHub Releases
    - The `1.0.0-alpha.1` release has been published on PyPI

- 🤖 Run the `test-execution-workflow` workflow on the `feature/#3-**` branch
    - All tests passed

## Adding New Functionality

- 🌿 Create a branch named `feature/#4-add-multiple-function` (later `feature/#4-**`) from the commit `feat: add read logic (#3)` (hash `abc8`, tag `1.0.0-alpha.1`) on the `develop` branch
- 📝 Create the commit `feat: #4: add a multiple function` (hash `abc9`):
    ```python
    function multiplication(number1, number2):
        multiplied = number1 * number2
        return multiplied
    ```
- 📝 Create a commit `test: #4: add a test to verify the logic for multiple function` (hash `abc10`):
    ```python
    function test_multiplication():
        result = multiplication(2, 3):

        check result = 6
    ```
- ➡️ Push the commits `feat: #4: add a multiple function` (hash `abc9`) and `test: #4: add a test to verify the logic for multiple function` (hash `abc10`) to the `feature/#4-**` branch:
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Running the `.reusable-semantic-release-workflow` workflow on the `feature/#4-**` branch; a **feature** release with the tag `1.0.0-sha-abc9` is expected
    - Commit `abc9` is tagged with `1.0.0-sha-abc9`
    - Commit `abc10` is not tagged
    - The `1.0.0-sha-abc9` release has appeared in GitHub Releases
    - The `1.0.0-sha-abc9` release has been published on PyPI

- 🤖 The `test-execution-workflow` is triggered on the `feature/#4-**` branch; tests are expected to run
    - All tests passed

- 🔗 Creating a PR (#4):
    - Commit message: `feat: #4: add a multiple function`
    - `feature/#4-**` -> `develop`
    - Squash merge

- Merged commit `feat: #4: add a multiple function (#4)` (hash `abc11`) into `develop`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Run the `.reusable-semantic-release-workflow` workflow on the `develop` branch; an **alpha** release with the tag `1.0.0-alpha.2` is expected
    - Commit `abc11` is tagged with `1.0.0-alpha.2`
    - The `1.0.0-alpha.2` release has appeared in GitHub Releases
    - The `1.0.0-alpha.2` release has been published on PyPI

- 🤖 Run the `test-execution-workflow` workflow on the `develop` branch; tests are expected to run
    - All tests passed

## New Stable Release

- 🌿 Create the `release/1.0.0` branch from the commit `feat: add a multiple function (#4)` (hash `abc11`, tag `1.0.0-alpha.2`) on the `develop` branch
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Running the `.reusable-semantic-release-workflow` workflow on the `release/1.0.0` branch; an **release candidate** release with the tag `1.0.0-rc.1` is expected
    - Commit `abc11` is tagged with `1.0.0-rc.1`
    - The `1.0.0-rc.1` release has appeared in GitHub Releases
    - The `1.0.0-rc.1` release has been published on PyPI

- 🤖 Run the `test-execution-workflow` workflow on the `release/1.0.0` branch; tests are expected to run
    - All tests passed

- 🔗 Creating a PR (#5):
    - Commit message `chore: release 1.0.0`
    - `release/1.0.0` -> `master`
    - Merge commit

- Merge the `chore: release 1.0.0` commit (hash `abc12`) into `master`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Run the `.reusable-semantic-release-workflow` workflow on the `master` branch; a **stable** release tagged `1.0.0` is expected
    - Commit `abc11` is tagged `1.0.0`
    - The `1.0.0` release has appeared in GitHub Releases
    - The `1.0.0` release has been published on PyPI

    <!-- [?] Where will the tag be applied? To `abc11` or `abc12`? -->

- 🤖 The `test-execution-workflow` is running on the `master` branch; tests are expected to run
    - All tests passed

<!-- [?] Do we want to run tests on the master branch? -->

## Updating `develop` after a new stable release

- 🔗 Creating a PR (#6):
    - Commit message: `chore: merge master to develop`
    - `master` -> `develop`
    - Merge commit

- Merge the commit `chore: merge master to develop` (hash `abc13`) into `develop`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Run the `.reusable-semantic-release-workflow` workflow on the `develop` branch; It is expected that the new release will **not** be published

- 🤖 Run the `test-execution-workflow` workflow on the `develop` branch; tests are expected to run
    - All tests passed

## Planned Fix

- 🌿 Create a branch named `feature/#5-fix-error-caused-by-incorrect-input-type-in-reads-number-from-console-function` (later`feature/#5-**`) from the commit `chore: merge master to develop` (hash `abc13`) on the `develop` branch
- 📝 Create the commit `test: #5: add a test to verify the error-raising logic for the function that reads a number from the console` (hash `abc14`):
    ```python
    function test_raise_exception_on_case_of_incorrect_type_in_console_number_reading_function():
        handle_exception(TypeError):
            catch_call read_from_console() return "j":
                result = read_number_from_console_and_return_it()
    ```
- 📝 Creating a commit `fix: #5: fix error caused by incorrect input type in reads_number_from_console function` (hash `abc15`):
    ```python
    function read_number_from_console_and_return_it():
        number = read_from_console()

        if type(number) != int:
            raise TypeError("Invalid input type")

        return number
    ```
- ➡️ Push the commits `test: #5: add a test to verify the raise error logic for the read_number_from_console function` (hash `abc14`) and `fix: #5: fix error caused by incorrect input type in the read_number_from_console function` (hash `abc15`) to the `feature/#5-**` branch:
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 The `.reusable-semantic-release-workflow` workflow is triggered on the `feature/#5-**` branch; a **feature** release with the tag `1.0.0-sha-abc15` is expected
    - Commit `abc14` is not tagged
    - Commit `abc15` is tagged with `1.0.0-sha-abc15`
    - The `1.0.0-sha-abc15` release has appeared in GitHub Releases
    - The `1.0.0-sha-abc15` release has been published on PyPI

- 🤖 Running the `test-execution-workflow` on the `feature/#5-**` branch; tests are expected to run
    - All tests passed

- 🔗 Creating a PR (#7):
    - Commit message: `fix: #5: fix error caused by incorrect input type in reads number from console function`
    - `feature/#5-**` -> `develop`
    - Squash merge

- Merged commit `fix: #5: fix error caused by incorrect input type in reads number from console function (#7)` (hash `abc16`) into `develop`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 The `.reusable-semantic-release-workflow` workflow is triggered on the `develop` branch; an **alpha** release tagged `1.0.1-alpha.1` is expected
    - Commit `abc16` was tagged `1.0.1-alpha.1`
    - The `1.0.1-alpha.1` release has appeared in GitHub Releases
    - The `1.0.1-alpha.1` release has been published on PyPI

- 🤖 Run the `test-execution-workflow` workflow on the `develop` branch; tests are expected to run
    - All tests passed

## Hotfix Case

- 🌿 Create the branch `hotfix/#6-fix-error-caused-by-incorrect-input-type-in-multiple-function` (hereinafter `hotfix/#6-**`) from the commit `chore: release 1.0.0` (hash `abc12`) on the `master` branch
- 📝 Create the commit `test: #6: add a test to verify the raise error logic for multiple function` (hash `abc17`):
    ```python
    function test_raise_exception_on_incorrect_type_in_multiplication_function():
        handle_exception(TypeError):
            result = multiplication("j", 5)
    ```
- 📝 Create a commit `fix: #6: fix error caused by incorrect input type in multiple function` (hash `abc18`):
    ```python
    function multiplication(number1, number2):
        if type(number1) != int or type(number2) != int:
            raise TypeError("Incorrect input type")
            
        product = number1 * number2
        return product
    ```
- ➡️ Push the commits `test: #6: add a test to verify the raise error logic for multiple function` (hash `abc17`) and `fix: #6: fix error caused by incorrect input type in multiple function` (hash `abc18`) to the `hotfix/#6-**` branch:
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 Running the `.reusable-semantic-release-workflow` workflow on the `hotfix/#6-**` branch; a **hotfix** release with the tag `1.0.1-hotfix-**.1` is expected

    <!-- [?] What does the tag for **hotfix** releases look like? -->

    - Commit `abc17` is not tagged
    - Commit `abc18` is tagged with `1.0.1-hotfix-**.1`
    - The `1.0.1-hotfix-**.1` release has appear in GitHub Releases
    - The `1.0.1-hotfix-**.1` release has been published on PyPI

- 🤖 Running the `test-execution-workflow` on the `hotfix/#6-**` branch; tests are expected to run
    - All tests passed

- 🔗 Creating a PR (#8):
    - Commit message: `fix: #6: fix error caused by incorrect input type in multiple function`
    - `hotfix/#6-**` -> `master`
    - Merge commit

- Merged the commit `fix: #6: fix error caused by incorrect input type in multiple function` (hash `abc19`) into `master`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 The `.reusable-semantic-release-workflow` workflow was triggered on the `master` branch; a **stable** release tagged `1.0.1` is expected
    - Commit `abc19` was tagged `1.0.1`
    - The `1.0.1` release has appeared in GitHub Releases
    - The `1.0.1` release has been published on PyPI

- 🤖 Run the `test-execution-workflow` workflow on the `master` branch; tests are expected to run
    - All tests passed

## Updating `develop` compared to `master`

- 🔗 Creating a PR (#9):
    - Commit message `fix: #6: fix error caused by incorrect input type in multiple function`
    - `master` -> `develop`
    - Merge commit

- Merging commit `fix: #6: fix error caused by incorrect input type in multiple function` (hash `abc20`) into `develop`
    - _GitHub Actions are triggered_

_GitHub Actions_
- 🤖 The `.reusable-semantic-release-workflow` is triggered on the `develop` branch; It is expected that the new release will **not** be published