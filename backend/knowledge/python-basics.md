# Python 基础

## 核心概念

Python 是一门语法简洁、上手较快的编程语言。它常用于脚本编写、Web 后端、数据处理、自动化和人工智能相关开发。

Python 的特点是表达直接，很多基础操作都有内置语法或标准库支持。

## 变量和类型

Python 中变量不需要提前声明类型。

```python
name = "Tom"
age = 18
```

变量名绑定到对象，类型属于对象本身。

## 列表

列表用于保存一组有序数据。

```python
numbers = [1, 2, 3]
numbers.append(4)
```

列表可以通过下标访问：

```python
first = numbers[0]
```

## 字典

字典用于保存键值对。

```python
user = {
    "name": "Tom",
    "age": 18,
}
```

通过 key 访问 value：

```python
print(user["name"])
```

## 函数

函数使用 `def` 定义。

```python
def add(a, b):
    return a + b
```

函数可以让代码复用，也能让程序结构更清晰。

## 模块

模块是 Python 组织代码的基本方式。一个 `.py` 文件就可以作为模块。

```python
import math
print(math.sqrt(16))
```

也可以从模块中导入指定内容：

```python
from math import sqrt
```

## 异常处理

异常用于处理程序运行时可能出现的错误。

```python
try:
    value = int("abc")
except ValueError:
    print("转换失败")
```

`try/except` 可以避免程序因为可预期错误直接中断。

## 常见误区

第一个误区是忽略缩进。Python 使用缩进表示代码块，缩进错误会导致语法错误或逻辑错误。

第二个误区是混淆列表和字典。列表适合有序数据，字典适合通过 key 查找数据。

第三个误区是把异常处理当成隐藏错误。异常处理应该让错误更可控，而不是静默吞掉所有问题。
