# Code examples for the diagram

## infra: #1: initialize project

```diff
# main.py

def main():
    return 0


if __name__ == "__main__":
    main()
```

## infra: #1 (Squash commit)

[infra: #1: initialize project](#infra-initialize-project)  

## feat: #3

```diff
# main.py

+ def addition(a: int, b: int) -> int:
+   return a - b
```

## feat: #3 (Squash commit)

[feat: #3](#feat-3)  

## docs: #4

```diff
# README.md

+ ## Methods
+ | Method | Function | Description |
+ | --- | --- | --- |
+ | Addition | addition(a: int, b: int) | Adds the numbers `a` and `b` and returns the sum |
```

## docs: #4 (Squash commit)

[docs: #4](#docs-4)  

## chore: #5

```diff
# main.py

- def addition(a: int, b: int) -> int:
+ def add(a: int, b: int) -> int:
```

## feat: #5

```diff
# main.py

+ def subtraction(a: int, b: int) -> int:
+   return b - a
```

## fix: #5

```diff
# main.py

def addition(a: int, b: int) -> int:
-   return a - b
+   return a + b
```

## feat!: #5

```diff
# main.py

- def add(a: int, b: int) -> int:
+ def addition(a: int, b: int) -> int:
```

## fix: #5 (Squash commit)

[chore: #5](#chore-5)  
[feat: #5](#feat-5)  
[fix: #5](#fix-5)  
[feat!: #5](#feat-5-1)  

## fix: #6

```diff
# main.py

def subtraction(a: int, b: int) -> int:
-   return b - a
+   return a - b
```

## fix: #6 (Squash commit)

[fix: #6](#fix-6)  

## feat: #7

```diff
# main.py

+ def multiplication(a: int, b: int) -> int:
+   return a * b
```

## feat: #7 (Squash commit)

[feat: #7](#feat-7)  

## feat: #8

```diff
# main.py

+ def division(a: int, b: int) -> int:
+   return a / b
```

## feat: #8 (Squash commit)

[feat: #8](#feat-8)  

## fix: #9

```diff
# main.py

def division(a: int, b: int) -> int:
-   return a / b
+   if b == "0":
+       raise ValueError("The divisor cannot be zero")
+
+   return a / b
```

## fix: #9 (Squash commit)

[fix: #9](#fix-9)  

## fix: #10

```diff
# main.py

def division(a: int, b: int) -> int:
-   if b == "0":
-       raise ValueError("The divisor cannot be zero")
-
-   return a / b
+   if b == 0:
+       raise ValueError("The divisor cannot be zero")
+
+   return a / b
```

## fix: #10 (Squash commit)

[fix: #10](#fix-10)

## feat: #11

```diff
# main.py

+ def read_number_from_console_and_return_it() -> int:
+   number = input("Input number")
+   return number
```

## feat: #11 (Squash commit)

[feat: #11](#feat-11)  