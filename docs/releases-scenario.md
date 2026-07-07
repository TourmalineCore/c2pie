# Releases scenario

1. Создание репозитория
1. Создание коммита `Initial commit` (хеш `abc1`):
    .gitattributes

1. Пуш коммита `Initial commit` (хеш `abc1`) в `master`

1. Создание ветки `develop` от коммита `Initial commit` (хеш `abc1`)

<!-- Добавление semantic release воркфлоу -->
1. Создание ветки `feature/add-semantic-release-workflow` от ветки `develop` от коммита `Initial commit` (хеш `abc1`)

1. Создание коммита `ci: add semantic release workflow` (хеш `abc2`):
    github/workflows/.reuseable-semantic-release-workflow.yml

1. Пуш коммита `ci: add semantic release workflow` (хеш `abc2`) в `feature/add-semantic-release-workflow`

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-semantic-release-workflow` 
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc2`
1. Коммит c хешем `abc2` помечен тегом `1.0.0-sha-abc2`
1. Появляется релиз `1.0.0-sha-abc2`
    ~ В PyPI публикуется релиз `0.2.0-sha-abc2`

[?] Кажется, что начать с версии `0.1.0-sha-abc2` невозможно, поэтому стартуем с `1.0.0-sha-abc2`

1. Создание PR#1 с заголовком `ci: add semantic release workflow` из `feature/add-semantic-release-workflow` в `develop`
1. Squash merge PR `ci: add semantic release workflow` в `develop`
1. В `develop` ветке появляется коммит `ci: add semantic release workflow (#1)` (хеш `abc3`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop` 
    => ожидаем, что новая версия не будет выпущена

<!-- Добавление воркфлоу запуска тестов -->
1. Создание ветки `feature/add-test-execution-workflow` от ветки `develop` от коммита `ci: add semantic release workflow (#1)` (хеш `abc3`)

1. Создание коммита `ci: add test execution workflow` (хеш `abc4`):
    github/workflows/test-execution-workflow.yml

1. Пуш коммита `ci: add test execution workflow` (хеш `abc4`) в `feature/add-test-execution-workflow`

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-test-execution-workflow`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc4`
1. Коммит c хешем `abc4` помечен тегом `1.0.0-sha-abc4`
1. Появляется релиз `1.0.0-sha-abc4`
    ~ В PyPI публикуется релиз `0.2.0-sha-abc4`

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-test-execution-workflow`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (0 tests found)

1. Создание PR#2 с заголовком `ci: add test execution workflow` из `feature/add-test-execution-workflow` в `develop`
1. Squash merge PR `ci: add test execution workflow` в `develop`
1. В `develop` ветке появляется коммит `ci: add test execution workflow (#2)` (хеш `abc5`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop` 
    => ожидаем, что новая версия не будет выпущена

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-test-execution-workflow`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (0 tests found)

<!-- Кейс добавления нового функционала параллельно `feature/add-test-execution-workflow` -->
1. Создание ветки `feature/add-read-logic` от ветки `develop` от коммита `ci: add semantic release workflow (#1)` (хеш `abc3`)

1. Создание коммита `test: add a test to verify the logic for reading data from the console` (хеш `abc6`), пуш в ветку `feature/add-read-logic`
```python
функция тест_на_логику_считывания_числа_с_консоли():
    отловить_вызов считать_с_консоли() вернуть 5:
        результат = считать_число_с_консоли_и_вернуть_его()

    проверить результат равен 5
```

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-read-logic`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc6`
1. Коммит c хешем `abc6` помечен тегом `1.0.0-sha-abc6`
1. Появляется релиз `1.0.0-sha-abc6`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc6`

1. Создание коммита `feat: add read logic with printing` (хеш `abc7`), пуш в ветку `feature/add-read-logic`
```python
функция считать_число_с_консоли_и_вернуть_его():
    число = считать_с_консоли()
    вернуть число

функция main():
    число = считать_число_с_консоли_и_вернуть_его()
    вывести(число)

    вернуть 0
```

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-read-logic`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc7`
1. Коммит c хешем `abc7` помечен тегом `1.0.0-sha-abc7`
1. Появляется релиз `1.0.0-sha-abc7`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc7`

1. Создание PR#3 с заголовком `feat: add read logic` из `feature/add-read-logic` в `develop`
1. Squash merge PR `feat: add read logic` в `develop`
1. В `develop` ветке появляется коммит `feat: add read logic (#3)` (хеш `abc8`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop`
    => ожидаем выпуск новой **alpha** версии с тегом `1.0.0-alpha.1`
1. Коммит c хешем `abc8` помечен тегом `1.0.0-alpha.1`
1. Появляется релиз `1.0.0-alpha.1`
    ~ В PyPI публикуется релиз `1.0.0-alpha.1`

<!-- Кейс добавления функционала -->
1. Создание ветки `feature/add-multiple-function` от ветки `develop` от коммита `feat: add read logic (#3)` (хеш `abc8`)

1. Коммит `feat: add a multiple function` (хеш `abc9`)
```python
функция умножение(число1, число2):
    произведение = число1 * число2
    вернуть произведение
```

1. Коммит `test: add a test to verify the logic for multiple function` (хеш `abc10`)
```python
функция тест_на_умножение():
    результат = умножение(2, 3):

    проверить результат равен 6
```

1. Пуш коммитов `feat: add a multiple function` (хеш `abc9`) и `test: add a test to verify the logic for multiple function` (хеш `abc10`) в `feature/add-multiple-function`.

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc9`
1. Коммит c хешем `abc9` помечен тегом `1.0.0-sha-abc9`
1. Появляется релиз `1.0.0-sha-abc9`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc9`
1. Коммит с хешем `abc10` не помечен тегом.

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

1. Создание PR#4 с заголовком `feat: add a multiple function` из `feature/add-multiple-function` в `develop`
1. Squash merge PR `feat: add a multiple function` в `develop`
1. В `develop` ветке появляется коммит `feat: add a multiple function (#4)` (хеш `abc11`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop`
    => ожидаем выпуск новой **alpha** версии с тегом `1.0.0-alpha.2`
1. Коммит c хешем `abc11` помечен тегом `1.0.0-alpha.2`
1. Появляется релиз `1.0.0-alpha.2`
    ~ В PyPI публикуется релиз `1.0.0-alpha.2`

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

<!-- Кейс релиза -->
1. Создание ветки `release/1.0.0` от коммита `feat: add a multiple function (#4)` (хеш `abc11`, тег `1.0.0-alpha.2`) из `develop`.

1. Запуск semantic release воркфлоу на ветке `release/1.0.0`
    => ожидаем выпуск новой **release candidate** версии с тегом `1.0.0-rc.1`
1. Коммит c хешем `abc11` помечен тегом `1.0.0-rc.1`
1. Появляется релиз `1.0.0-rc.1`
    ~ В PyPI публикуется релиз `1.0.0-rc.1`

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

1. Создание PR#5 с заголовком `chore: release 1.0.0` из `release/1.0.0` в `master`
1. Merge commit PR `chore: release 1.0.0` из `release/1.0.0` в `master`
1. В `master` ветке появляется коммит `chore: release 1.0.0` (хеш `abc12`)

1. Запуск semantic release воркфлоу на ветке `master`
    => ожидаем выпуск новой **stable** версии с тегом `1.0.0`
1. Коммит c хешем `abc11` помечен тегом `1.0.0`

[?] Куда будет помещен тег? На abc11 или abc12?

1. Появляется релиз `1.0.0`
    ~ В PyPI публикуется релиз `1.0.0`

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

[?] Хотим ли мы запускать тесты на master-ветке?

<!-- Актуализация develop после выпуска нового stable релиза -->
1. Создание PR#6 с заголовком `chore: merge master to develop` из `master` в `develop`
1. Merge commit PR `chore: merge master to develop` из `master` в `develop`
1. В `develop` ветке появляется коммит `chore: merge master to develop` (хеш `abc13`)

1. Запуск semantic release воркфлоу на ветке `master`
    => ожидаем, что новый релиз не будет выпущен

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

<!-- Кейс планового фикса -->
1. Создание ветки `feature/fix-error-caused-by-incorrect-input-type-in-reads-number-from-console-function` от ветки `develop` от коммита `chore: merge master to develop` (хеш `abc13`)

1. Создание коммита `test: add a test to verify the raise error logic for reads number from console function` (хеш `abc14`)
```python
функция тест_вызова_исключения_в_случае_некорректного_типа_в_функции_считывания_числа_с_консоли():
    учесть вызвано_исключение(Ошибка_типа):
        отловить_вызов считать_с_консоли() вернуть "j":
            результат = считать_число_с_консоли_и_вернуть_его()
```

1. Создание коммита `fix: fix error caused by incorrect input type in reads number from console function` (хеш `abc15`)
```python
функция считать_число_с_консоли_и_вернуть_его():
    число = считать_с_консоли()

    если тип(число) != int:
        вызвать_исключение Ошибка_типа("Неккоректный тип входного значения")

    вернуть число
```

1. Пуш коммитов `test: add a test to verify the raise error logic for reads number from console function` (хеш `abc14`) и `fix: fix error caused by incorrect input type in reads number from console function` (хеш `abc15`) в `feature/fix-error-caused-by-incorrect-input-type-in-reads-number-from-console-function`

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc15`
1. Коммит с хешем `abc14` не помечен тегом.
1. Коммит c хешем `abc15` помечен тегом `1.0.0-sha-abc15`
1. Появляется релиз `1.0.0-sha-abc15`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc15`

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

1. Создание PR#6 с заголовком `fix: fix error caused by incorrect input type in reads number from console function` из `feature/fix-error-caused-by-incorrect-input-type-in-reads-number-from-console-function` в `develop`
1. Squash merge PR `fix: fix error caused by incorrect input type in reads number from console function` в `develop`
1. В `develop` ветке появляется коммит `fix: fix error caused by incorrect input type in reads number from console function (#6)` (хеш `abc16`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop`
    => ожидаем выпуск новой **alpha** версии с тегом `1.0.1-alpha.1`
1. Коммит c хешем `abc16` помечен тегом `1.0.1-alpha.1`
1. Появляется релиз `1.0.1-alpha.1`
    ~ В PyPI публикуется релиз `1.0.1-alpha.1`

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

<!-- Кейс хотфикса -->
1. Создание ветки `hotfix/fix-error-caused-by-incorrect-input-type-in-multiple-function` от ветки `master` от коммита `chore: release 1.0.0` (хеш `abc12`)

1. Создание коммита `test: add a test to verify the raise error logic for multiple function` (хеш `abc17`)
```python
функция тест_вызова_исключения_в_случае_некорректного_типа_в_функции_умножения():
    учесть вызвано_исключение(Ошибка_типа):
        результат = умножение("j", 5)
```

1. Создание коммита `fix: fix error caused by incorrect input type in multiple function` (хеш `abc18`)
```python
функция умножение(число1, число2):
    если тип(число1) != int или тип(число2) != int:
        вызвать_исключение Ошибка_типа("Неккоректный тип входного значения")
        
    произведение = число1 * число2
    вернуть произведение
```

1. Пуш коммитов `test: add a test to verify the raise error logic for multiple function` (хеш `abc17`) и `fix: fix error caused by incorrect input type in multiple function` (хеш `abc18`) в `hotfix/fix-error-caused-by-incorrect-input-type-in-multiple-function`

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `hotfix/fix-error-caused-by-incorrect-input-type-in-multiple-function`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc18`
1. Коммит с хешем `abc17` не помечен тегом.
1. Коммит c хешем `abc18` помечен тегом `1.0.0-sha-abc18`
1. Появляется релиз `1.0.0-sha-abc18`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc18`

1. Запуск `test-execution-workflow` воркфлоу на ветке `hotfix/fix-error-caused-by-incorrect-input-type-in-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

1. Создание PR#7 с заголовком `fix: fix error caused by incorrect input type in multiple function` из `hotfix/fix-error-caused-by-incorrect-input-type-in-multiple-function` в `master`
1. Merge commit PR `fix: fix error caused by incorrect input type in multiple function` в `master`
1. В `master` ветке появляется коммит `fix: fix error caused by incorrect input type in multiple function (#7)` (хеш `abc19`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop`
    => ожидаем выпуск новой **stable** версии с тегом `1.0.1`
1. Коммит c хешем `abc19` помечен тегом `1.0.1`
1. Появляется релиз `1.0.1`
    ~ В PyPI публикуется релиз `1.0.1`

1. Запуск `test-execution-workflow` воркфлоу на ветке `feature/add-multiple-function`
    => ожидаем запуск тестов
1. Запуск тестов завершился кодом 0 (all test passed)

<!-- Мерже в девелом -->

<!-- Кейс добавления функционала в параллельной ветке + с ошибкой -->
1. Создание ветки `feature/add-subtraction-function` от ветки `develop` от коммита `feat: add read logic (#2)` (хеш `abc6`)

<!-- Умышленно опущено добавление теста, разработчик забыл -->

1. Коммит `feat: add a subtraction function` (хеш `abc10`)
```python
функция вычитание(число1, число2):
    разница = число2 - число1 # Нарушен порядок
    вернуть разница
```

1. Пуш коммита `feat: add a subtraction function` (хеш `abc10`) в `feature/add-subtraction-function`.

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-subtraction-function`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc10`
1. Коммит c хешем `abc10` помечен тегом `1.0.0-sha-abc10`
1. Появляется релиз `1.0.0-sha-abc10`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc10`

1. Создание PR#4 с заголовком `feat: add a subtraction function` из `feature/add-subtraction-function` в `develop`
1. Squash merge PR `feat: add a subtraction function` в `develop`
1. В `develop` ветке появляется коммит `feat: add a subtraction function (#4)` (хеш `abc11`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop`
    => ожидаем выпуск новой **alpha** версии с тегом `1.0.0-alpha.3`
1. Коммит c хешем `abc11` помечен тегом `1.0.0-alpha.3`
1. Появляется релиз `1.0.0-alpha.3`
    ~ В PyPI публикуется релиз `1.0.0-alpha.3`

<!-- Кейс фикса ошибки -->
1. Создание ветки `feature/fix-subtraction-order-error` от ветки `develop` от коммита `feat: add a subtraction function (#4)` (хеш `abc11`)

1. Коммит `test: add a test to verify the logic for subtraction function` (хеш `abc12`)
```python
функция тест_на_вычитание():
    результат = вычитание(10, 5):

    проверить результат равен 5
```

<!-- 1. Коммит `fix: add a test to verify the logic for subtraction function` (хеш `abc12`)
```python
функция тест_на_вычитание():
    результат = вычитание(10, 5):

    проверить результат равен 5
``` -->

1. Пуш коммита `feat: add a subtraction function` (хеш `abc10`) в `feature/add-subtraction-function`.

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `feature/add-subtraction-function`
    => ожидаем выпуск новой **feature** версии с тегом `1.0.0-sha-abc10`
1. Коммит c хешем `abc10` помечен тегом `1.0.0-sha-abc10`
1. Появляется релиз `1.0.0-sha-abc10`
    ~ В PyPI публикуется релиз `1.0.0-sha-abc10`

1. Создание PR#4 с заголовком `feat: add a subtraction function` из `feature/add-subtraction-function` в `develop`
1. Squash merge PR `feat: add a subtraction function` в `develop`
1. В `develop` ветке появляется коммит `feat: add a subtraction function (#4)` (хеш `abc11`)

1. Запуск `.reuseable-semantic-release-workflow` воркфлоу на ветке `develop`
    => ожидаем выпуск новой **alpha** версии с тегом `1.0.0-alpha.3`
1. Коммит c хешем `abc11` помечен тегом `1.0.0-alpha.3`
1. Появляется релиз `1.0.0-alpha.3`
    ~ В PyPI публикуется релиз `1.0.0-alpha.3`







---

1. Создание ветки `feature/add-read-logic` от ветки `develop` от коммита `Initial commit` (хеш `abc1`, тег `0.1.0`)
1. Пуш коммита `test: Add a test to verify the logic for reading data from the console` (хеш `abc2`)
```python
функция тест_на_логику_считывания_с_консоли():
    отловить_вызов считать_с_консоли() вернуть 5:
        результат = считать_с_консоли()

    проверить результат равен 5
```

1. semantic release воркфлоу **не** запускается

1. Пуш коммита `feat: add read logic with following print` (хеш `abc3`) в ветку `feature/add-read-logic`.
```python
функция считать_число_с_консоли_и_вернуть_его():
    число1 = считать_с_консоли()
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