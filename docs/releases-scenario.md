# Releases scenario

1. Создание репозитория
1. Создание коммита `Initial commit` (хеш `abc1`):
    .gitattributes

1. Пуш коммита `Initial commit` (хеш `abc1`) в `master`

<!-- 1. Запуск semantic release воркфлоу на ветке `master` => ожидаем выпуск новой **stable** версии
1. Коммит c хешем `abc1` помечен тегом `0.1.0`
1. Появляется релиз `0.1.0`
    ~ В PyPI публикуется релиз `0.1.0` -->

1. Создание ветки `develop` от коммита `Initial commit` (хеш `abc1`)
1. Создает ветку `feature/add-semantic-release-workflow` от ветки `develop` от коммита `Initial commit` (хеш `abc1`)

1. Создание коммита `ci: add semantic release workflow` (хеш `abc2`):
    .reuseable-semantic-release-workflow
1. Пуш коммита `ci: add semantic release workflow` (хеш `abc2`) в `feature/add-semantic-release-workflow`

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-semantic-release-workflow` 
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc2`
1. Коммит c хешем `abc2` помечен тегом `1.0.0-sha-abc2`
1. Появляется релиз `1.0.0-sha-abc2`
    ~ В PyPI публикуется релиз `0.2.0-sha-abc2`

[?] Кажется, что начать с версии `0.1.0-sha-abc2` невозможно, поэтому стартуем с `1.0.0-sha-abc2`

1. Создание PR#1 с заголовком `ci: add semantic release workflow` из `feature/add-semantic-release-workflow` в `develop`
1. Squash merge PR `ci: add semantic release workflow` в `develop`
1. В `develop` ветке появляется коммит `ci: add semantic release workflow (#1)` (хеш `abc3`, тег `1.0.0-alpha.1`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop` 
    => ожидаем, что новая версия не будет выпущена

1. Создание ветки `feature/add-read-logic` от ветки `develop` от коммита `ci: add semantic release workflow (#1)` (хеш `abc3`)
1. Пуш коммита `test: add a test to verify the logic for reading data from the console` (хеш `abc4`)
```python
функция тест_на_логику_считывания_с_консоли():
    отловить_вызов считать() вернуть 5:
        результат = считать()

    проверить результат равен 5
```

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-read-logic`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc4`
1. Коммит c хешем `abc4` помечен тегом `1.0.0-sha-abc4`
1. Появляется релиз `1.0.0-sha-abc4`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc4`


1. Пуш коммита `feat: add read logic with printing` (хеш `abc5`) в ветку `feature/add-read-logic`.
```python
функция считать_число_с_консоли_и_вернуть_его():
    число1 = считать()
    вернуть число1

функция main():
    число = считать_число_с_консоли_и_вернуть_его()
    вывести(число)

    вернуть 0
```

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-read-logic`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc5`
1. Коммит c хешем `abc5` помечен тегом `1.0.0-sha-abc5`
1. Появляется релиз `1.0.0-sha-abc5`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc5`

1. Создание PR#2 с заголовком `feat: add read logic` из `feature/add-read-logic` в `develop`
1. Squash merge PR `feat: add read logic` в `develop`
1. В `develop` ветке появляется коммит `feat: add read logic (#2)` (хеш `abc6`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop`
    => ожидаем выпуск новой **alpha** версии с тегом `1.0.0-alpha.1`
1. Коммит c хешем `abc6` помечен тегом `1.0.0-alpha.1`
1. Появляется релиз `1.0.0-alpha.1`
    ~ В PyPI публикуется релиз `1.0.0-alpha.1`




---

1. Создание ветки `feature/add-read-logic` от ветки `develop` от коммита `Initial commit` (хеш `abc1`, тег `0.1.0`)
1. Пуш коммита `test: Add a test to verify the logic for reading data from the console` (хеш `abc2`)
```python
функция тест_на_логику_считывания_с_консоли():
    отловить_вызов считать() вернуть 5:
        результат = считать()

    проверить результат равен 5
```

1. semantic release воркфлоу **не** запускается

1. Пуш коммита `feat: add read logic with following print` (хеш `abc3`) в ветку `feature/add-read-logic`.
```python
функция считать_число_с_консоли_и_вернуть_его():
    число1 = считать()
    вернуть число1

функция main():
    число = считать_число_с_консоли_и_вернуть_его()
    вывести(число)

    вернуть 0
```

1. Запуск semantic release воркфлоу на ветке `feature/add-read-logic` => ожидаем выпуск новой **dev** версии
1. Коммит c хешем `abc3` помечен тегом `0.2.0-sha-abc3`
1. Появляется релиз `0.2.0-sha-abc3`
    ~ В PyPI публикуется релиз `0.2.0-sha-abc3`

1. Создание PR с заголовком `feat: add read logic` из `feature/add-read-logic` в `develop`
1. Squash merge PR `feat: add read logic` из `feature/add-read-logic` в `develop`
1. В `develop` ветке появляется коммит `feat: add read logic` (хеш `abc4`)

1. Запуск semantic release воркфлоу на ветке `develop` => ожидаем выпуск новой **alpha** версии
1. Коммит c хешем `abc4` помечен тегом `0.2.0-alpha.1`
1. Появляется релиз `0.2.0-alpha.1`
    ~ В PyPI публикуется релиз `0.2.0-alpha.1`

1. Создание ветки `release/0.2.0` от коммита `feat: add read logic` (хеш `abc4`, тег `0.2.0-alpha.1`) из `develop`.

1. Запуск semantic release воркфлоу на ветке `release/0.2.0` => ожидаем выпуск новой **release candidate** версии
1. Коммит c хешем `abc4` помечен тегом `0.2.0-rc.1`
1. Появляется релиз `0.2.0-rc.1`
    ~ В PyPI публикуется релиз `0.2.0-rc.1`

1. Создание PR с заголовком `chore: release 0.2.0` из `release/0.2.0` в `master`
1. Merge commit PR `chore: release 0.2.0` из `release/0.2.0` в `master`
1. В `master` ветке появляется коммит `chore: release 0.2.0` (хеш `abc5`)