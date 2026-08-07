# Workflows

## publish-release.yml

### Token

The standard `GITHUB_TOKEN` is tied to a specific workflow run and, when the branch is protected, is subject to the same rules as standard users. Therefore, a workflow that uses `GITHUB_TOKEN` will not be able to push any changes to a branch with the `Require a pull request before merging` rule enabled.

In addition, the standard token has another limitation: any events (push, tag creation, release publication) triggered via the standard `GITHUB_TOKEN` do not trigger other workflows that respond to those events - this is an intentional limitation imposed by GitHub to prevent infinite loops.

To provide the token with the necessary permissions to push to the protected branch and ensure that the `publish-package.yml` workflow trigger is executed when a new release is published, a PAT (Personal Access Token) named `C2PIE_SEMANTIC_RELEASE_GH_TOKEN` was created and added.

#### Generating a new token

**General**

| Field | Value |
| --- | --- |
| Token name | `C2PIE_SEMANTIC_RELEASE_GH_TOKEN` |
| Description (Optional) | * |
| Resource owner | TourmalineCore |
| Expiration | 366 days (or any if neccessary) |

**Repository access**

| Field | Value |
| --- | --- |
| Only select repositories | TourmalineCore/c2pie |

**Permissions**

> In the table header, select **Repositories**

| Permission | Access level |
| --- | --- |
| Contents | Read and write |
| Issues | Read and write |
| Metadata (Set up automatically) | Read only |
| Pull Requests | Read and write |

#### Adding a token to a repository

After generating the token, copy it. 

Further, go to the settings for the [`TourmalineCore/c2pie`](https://github.com/TourmalineCore/c2pie) repository, navigate to the `Secrets and variables` section, then to `Actions`, and add the generated token to the repository's secrets with the name `C2PIE_SEMANTIC_RELEASE_GH_TOKEN`.

