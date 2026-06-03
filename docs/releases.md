# Release Flow

Основным артефактом каждого релиза является `wheel` - формат дистрибутива Python-пакета. Каждый пуш коммита в релизные ветки триггерит GitHub Actions workflow, который запускает semantic-release, выпускает новый релиз по правилам из таблицы [версионирования](#версионирование) и публикует его в PyPI и GitHub Releases. Коммиты с `[skip ci]` в конце workflow игнорирует - именно поэтому backmerge-коммиты не создают новых релизов и не имеют тегов на диаграммах.

Changelog генерируется автоматически при каждом релизном событии: alpha, rc, stable, hotfix, maintenance. Для сохранения корректной истории в changelog PR в prerelease-ветки (`feature/*`, `release/*`, `hotfix/*`) необходиме мерджить без squash.

Так же changelog конкретной версии попадает в release notes к этой версии. 

| Ветка                  | Тип релиза                   | PyPI канал                     |
| ---------------------- | -----------------------------| ------------------------------ |
| `feature/*`            | Dev build (artifact)         | не публикуется                 |
| `develop`              | Pre-release (alpha)          | `--pre`                        |
| `release/*`            | Pre-release (rc)             | `--pre`                        |
| `master`               | Stable release               | `latest`                       |
| `hotfix/*` -> `master` | Stable release (patch)       | только прямым указанием версии |
| `1.x`                  | Stable release (maintenance) | только прямым указанием версии |

## Общая диаграмма

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit tag: "1.3.0"
   branch develop
   checkout develop
   branch feature/67-A
   checkout feature/67-A
   commit id: "fix: A" tag: "1.3.1-alpha.1-sha-a1"
   checkout develop
   branch feature/71-B
   checkout feature/71-B
   commit id: "feat: B" tag: "1.4.0-alpha.1-sha-b1"
   checkout develop
   merge feature/67-A tag: "1.3.1-alpha.1"
   commit id: "fix: bug" tag: "1.3.2-alpha.2"
   merge feature/71-B tag: "1.4.0-alpha.3"
   branch release/1.4.0
   checkout release/1.4.0
   commit id: "fix: edge case" tag: "1.4.0-rc.1"
   checkout develop
   merge release/1.4.0 id: "backmerge rc.1 [skip ci]"
   commit id: "feat: C" tag: "1.4.0-alpha.4"
   branch feature/80-D
   checkout feature/80-D
   commit id: "feat: D" tag: "1.4.0-alpha.4-sha-d1"
   checkout release/1.4.0
   commit id: "fix: typo" tag: "1.4.0-rc.2"
   checkout develop
   merge release/1.4.0 id: "backmerge rc.2 [skip ci]"
   checkout master
   merge release/1.4.0 tag: "1.4.0"
   checkout develop
   merge master id: "backmerge 1.4.0 [skip ci]"
   checkout master
   branch hotfix/crash
   checkout hotfix/crash
   commit id: "fix: smthn"
   checkout master
   merge hotfix/crash tag: "1.4.1"
   checkout develop
   merge master id: "backmerge hotfix [skip ci]"
   merge feature/80-D tag: "1.5.0-alpha.1"
```
## Dev Release

### Feature Dev Builds

Ветка `feature/*` создаётся от `develop`. Каждый пуш в `feature/*` запускает CI, который собирает wheel и сохраняет его как артефакт сборки (GitHub Actions artifact). Эти сборки не публикуются в PyPI и в GitHub Releases - они доступны только внутри workflow как артефакты.

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.3.0"
   branch develop
   checkout develop

   branch feature/67-A
   checkout feature/67-A
   commit id: "feat: A (push 1)" tag: "1.4.0-alpha.1-sha-a1"
   commit id: "feat: A (push 2)" tag: "1.4.0-alpha.1-sha-a2"
   commit id: "fix: A (push 3)" tag: "1.4.0-alpha.1-sha-a3"
```

Если feature-ветка создаётся от коммита с уже существующим alpha-тегом, тег dev-сборки будет содержать эту же base-версию:

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.3.0"
   branch develop
   checkout develop
   commit id: "feat: X" tag: "1.4.0-alpha.1"

   branch feature/80-D
   checkout feature/80-D
   commit id: "feat: D (push 1)" tag: "1.4.0-alpha.1-sha-d1"
   commit id: "feat: D (push 2)" tag: "1.4.0-alpha.1-sha-d2"
```

### Alpha Releases from develop

После мержа PR из `feature/*` в `develop` semantic-release автоматически публикует новый pre-release alpha.

Версия бампается один раз при первом коммите соответствующего типа, последующие коммиты того же типа только инкрементируют счётчик alpha:

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.0.0"
   branch develop
   checkout develop

   branch feature/fix-A
   checkout feature/fix-A
   commit id: "fix: A"
   checkout develop
   merge feature/fix-A tag: "1.0.1-alpha.1"

   branch feature/fix-B
   checkout feature/fix-B
   commit id: "fix: B"
   checkout develop
   merge feature/fix-B tag: "1.0.1-alpha.2"

   branch feature/feat-C
   checkout feature/feat-C
   commit id: "feat: C"
   checkout develop
   merge feature/feat-C tag: "1.1.0-alpha.1"

   branch feature/feat-D
   checkout feature/feat-D
   commit id: "feat: D"
   checkout develop
   merge feature/feat-D tag: "1.1.0-alpha.2"
```

Параллельные feature-ветки не мешают друг другу - каждый пуш генерирует независимую dev-сборку со своим SHA. Счётчик alpha на `develop` инкрементируется при каждом пуше (если есть необходимый [коммит](#Версионирование)):

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.3.0"
   branch develop
   checkout develop

   branch feature/67-A
   checkout feature/67-A
   commit id: "feat: A" tag: "1.4.0-alpha.1-sha-a1"

   checkout develop
   branch feature/71-B
   checkout feature/71-B
   commit id: "feat: B" tag: "1.4.0-alpha.1-sha-b1"

   checkout develop
   merge feature/67-A id: "Merge PR #67" tag: "1.4.0-alpha.1"
   merge feature/71-B id: "Merge PR #71" tag: "1.4.0-alpha.2"
```
## Release Candidate

`release/1.4.0` создаётся от `develop`.

> На ветке `release/*` вручную допускаются только `fix:`-коммиты. Это соглашение на уровне команды - автоматической проверки в CI пока нет (backlog). Так же не допускается существование нескольких `release/*` веток одновременно.

Backmerge - это автоматический merge изменений (`CHANGELOG.md`, `pyproject.toml`) из релизной ветки обратно в `develop` после каждого релизного шага. Пушится коммит с `[skip ci]`, чтобы не триггерить новый alpha. Если при backmerge возникают конфликты - semantic-release создаёт PR для ручного разрешения конфликта.

### Кейс 1 - RC только с внутренними фиксами

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.3.0"
   branch develop
   checkout develop
   commit id: "feat: A" tag: "1.4.0-alpha.1"

   branch release/1.4.0
   checkout release/1.4.0
   commit id: "fix: B" tag: "1.4.0-rc.1"

   checkout develop
   merge release/1.4.0 id: "backmerge rc.1 [skip ci]"
   commit id: "feat: C" tag: "1.4.0-alpha.2"

   checkout release/1.4.0
   commit id: "fix: D" tag: "1.4.0-rc.2"

   checkout develop
   merge release/1.4.0 id: "backmerge rc.2 [skip ci]"

   checkout master
   merge release/1.4.0 tag: "1.4.0"

   checkout develop
   merge master id: "backmerge 1.4.0 [skip ci]"
```

### Кейс 2 - RC с добавлением новых изменений с develop

Если в процессе RC нужно включить новые изменения из `develop` - ветка `release/*` ребейзится на `develop`.

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.3.0"
   branch develop
   checkout develop
   commit id: "feat: A" tag: "1.4.0-alpha.1"

   branch release/1.4.0
   checkout release/1.4.0
   commit id: "fix: B" tag: "1.4.0-rc.1"

   checkout develop
   merge release/1.4.0 id: "backmerge rc.1 [skip ci]"
   commit id: "feat: C" tag: "1.4.0-alpha.2"

   checkout release/1.4.0
   merge develop id: "rebase" tag: "1.4.0-rc.2"
   commit id: "fix: D" tag: "1.4.0-rc.3"

   checkout develop
   merge release/1.4.0 id: "backmerge rc.3 [skip ci]"

   checkout master
   merge release/1.4.0 tag: "1.4.0"

   checkout develop
   merge master id: "backmerge 1.4.0 [skip ci]"
```

### Кейс 3 - Backmerge с конфликтом

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.4.0-alpha.1"
   branch develop
   checkout develop
   commit id: "feat: conflicting change"

   branch release/1.4.0
   checkout release/1.4.0
   commit id: "fix: conflict commit" tag: "1.4.0-rc.1"

   checkout develop
   merge release/1.4.0 id: "resolve conflicts manually"
```

## Stable Release

`release/1.4.0` мержится в `master` через PR. semantic-release создаёт тег `v1.4.0` как stable. Backmerge доставляет в `develop` обновлённые `CHANGELOG.md` и `pyproject.toml` - новый alpha при этом не создаётся из-за тега `[skip ci]`. Так же создается PR если в backmerge из `master` в `develop` если возник конфликт.

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.3.0"
   branch develop
   checkout develop
   commit id: "feat: A" tag: "1.4.0-alpha.1"

   branch release/1.4.0
   checkout release/1.4.0
   commit id: "fix: B" tag: "1.4.0-rc.1"

   checkout develop
   merge release/1.4.0 id: "backmerge rc.1 [skip ci]"

   checkout release/1.4.0
   commit id: "fix: C" tag: "1.4.0-rc.2"

   checkout develop
   merge release/1.4.0 id: "backmerge rc.2 [skip ci]"

   checkout master
   merge release/1.4.0 id: "Release 1.4.0" tag: "1.4.0"

   checkout develop
   merge master id: "backmerge 1.4.0 [skip ci]"
   commit id: "feat: D" tag: "1.5.0-alpha.1"
```
## Hotfix

Хотфикс используется для критических багов в stable-релизах. Ветка `hotfix/*` создаётся напрямую от `master`, минуя `develop` и `release/*`. После мержа в `master` semantic-release публикует stable патч-релиз делает backmerge в `develop`.

> На ветке `hotfix/*` вручную допускаются только `fix:`-коммиты. Это соглашение на уровне команды - автоматической проверки в CI пока нет (backlog).

### Кейс 1 - баг и в master, и в develop

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.4.0"
   branch develop
   checkout develop
   commit id: "feat: E" tag: "1.5.0-alpha.1"

   checkout master
   branch hotfix/smthn
   checkout hotfix/smthn
   commit id: "fix: smthn"

   checkout master
   merge hotfix/smthn id: "Merge hotfix" tag: "1.4.1"

   checkout develop
   merge master id: "backmerge hotfix [skip ci]"
   commit id: "feat: F" tag: "1.5.0-alpha.2"
```

### Кейс 2 - баг в master, в develop уже пофикшен (конфликт в backmerge)

Если в `develop` баг уже исправлен иначе - backmerge создаёт конфликт. semantic-release открывает PR, который остаётся открытым для ручного разрешения конфликта.

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.4.0"
   branch develop
   checkout develop
   commit id: "feat: conflicting change"

   checkout master
   branch hotfix/fix
   checkout hotfix/fix
   commit id: "fix: overlapping area"
   checkout master
   merge hotfix/fix tag: "1.4.1"
   
   checkout develop
   merge master id: "resolve conflicts manually"
```
## Maintenance Release

Используется когда нужно патчить или добавлять фичи в старую мажорную версию, пока `master` уже ушёл вперёд. Maintenance-ветка не мержится обратно в `develop` или `master`. Все изменения вносятся через отдельные ветки + PR. semantic-release публикует maintenance релиз.

> Breaking changes в maintenance-ветках запрещены.

### Кейс 1 - fix и feat в старой мажорной версии

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
   commit id: "..." tag: "1.9.0"
   branch 1.x
   checkout 1.x

   checkout master
   commit id: "feat!: A" tag: "2.0.0"
   commit id: "feat: B" tag: "2.3.0"

   checkout 1.x
   branch fix/maintenance-bug
   checkout fix/maintenance-bug
   commit id: "fix: C"
   checkout 1.x
   merge fix/maintenance-bug id: "Merge fix PR" tag: "1.9.1"

   branch feat/maintenance-feature
   checkout feat/maintenance-feature
   commit id: "feat: D"
   checkout 1.x
   merge feat/maintenance-feature id: "Merge feat PR" tag: "1.10.0"
```

### Кейс 2 - баг и в master, и в 1.x

Фикс сначала выходит на `master`, затем добавляется в отдельную ветку и мержится в `1.x`.

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'} }}%%
gitGraph
commit id: "..." tag: "1.9.0"
branch 1.x
checkout master
commit tag: "2.0.0"
branch fix/shared-bug
commit id: "fix: bug"
checkout master
merge fix/shared-bug id: "Merge fix PR" tag: "2.0.1"
checkout 1.x
branch fix/shared-bug-1
checkout fix/shared-bug-1
commit id: "fix: shared bug"
checkout 1.x
merge fix/shared-bug-1 id: "Merge maintenance PR" tag: "1.9.1"
```

**Правила maintenance-веток:**
- Создаются только для мажорных версий: `1.x`, `2.x` и т.д.
- Ветка создаётся от последнего тега в этой мажорной линии (например от `v1.9.0`)
- Ветку нужно явно добавить в `branches` конфига `.releaserc`
- Допустимые коммиты: `fix:` и `feat:` (без breaking changes)
## Публикация пакета

| Тип релиза                           | GitHub Releases | PyPI          |
| ------------------------------------ | --------------- | ------------- |
| `1.4.0-alpha.1-sha-abc123` (feature) | -               | -             |
| `1.4.0-alpha.1` (develop)            | +               | + pre-release |
| `1.4.0-rc.1` (release/*)             | +               | + pre-release |
| `1.4.0` (master)                     | +               | + latest      |

## Версионирование

Только `feat`, `fix`, `docs` и `refactor` триггерят релиз. Все остальные коммиты (`chore`, `ci`, `style`, `test`, `build`, `config`) игнорируются semantic-release.

| Ветка       | Тип коммита                    | Bump        | Результат                 | Примечание                    |
| ----------- | ------------------------------ | ----------- | ------------------------- | ----------------------------- |
| `feature/*` | любой                          | sha         | `1.4.0-alpha.1-sha-<sha>` | artifact                      |
| `develop`   | `fix:` / `docs:` / `refactor:` | patch+alpha | `1.0.1-alpha.N`           | bump один раз, далее только N |
| `develop`   | `feat:`                        | minor+alpha | `1.1.0-alpha.N`           | bump один раз, далее только N |
| `release/*` | `fix:`                         | rc          | `1.4.0-rc.N`              | только fix:                   |
| `master`    | `fix:` / `docs:` / `refactor:` | patch       | `1.4.1`                   |                               |
| `master`    | `feat:`                        | minor       | `1.5.0`                   | включает все patch-изменения  |
| `master`    | `feat!:` / `BREAKING CHANGE`   | major       | `2.0.0`                   |                               |
| `1.x`       | `fix:`                         | patch       | `1.9.1`                   |                               |
| `1.x`       | `feat:`                        | minor       | `1.10.0`                  | без breaking changes          |

