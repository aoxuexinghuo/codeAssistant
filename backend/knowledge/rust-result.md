# Rust Result 错误处理

## 核心概念

Rust 使用 `Result` 表示可能成功也可能失败的操作。它比异常更显式，要求调用者处理错误。

`Result` 的定义可以理解为：

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`Ok` 表示成功，`Err` 表示失败。

## 基本使用

```rust
let result = std::fs::read_to_string("a.txt");
```

这个函数返回 `Result<String, Error>`，因为读取文件可能失败。

## match 处理

```rust
match result {
    Ok(content) => println!("{}", content),
    Err(error) => println!("{}", error),
}
```

`match` 能明确处理成功和失败两种情况。

## unwrap

```rust
let content = result.unwrap();
```

`unwrap` 会在成功时取出值，但失败时会直接 panic。

初学可以用它测试，但正式代码中要谨慎使用。

## expect

```rust
let content = result.expect("读取文件失败");
```

`expect` 和 `unwrap` 类似，但可以提供更清楚的错误信息。

## 问号运算符

```rust
fn read_file() -> Result<String, std::io::Error> {
    let content = std::fs::read_to_string("a.txt")?;
    Ok(content)
}
```

`?` 表示如果成功就取出值，如果失败就把错误返回给调用者。

## Option 和 Result 的区别

`Option` 表示有值或没有值。

`Result` 表示成功或失败，并且失败时带有错误原因。

如果需要知道为什么失败，应该使用 `Result`。

## 常见误区

第一个误区是到处使用 `unwrap`。这会让程序在错误发生时直接崩溃。

第二个误区是不理解 `?`。它不是忽略错误，而是把错误提前返回。

第三个误区是把 `Option` 和 `Result` 混用。缺少值用 `Option`，操作失败用 `Result`。
