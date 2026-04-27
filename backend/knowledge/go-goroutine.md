---
title: Go goroutine
topic: Go
level: beginner
tags: [goroutine, 并发, WaitGroup, channel]
---

# Go goroutine

## 核心概念

goroutine 是 Go 运行时管理的轻量级并发执行单元。它不是操作系统线程，但会被 Go 运行时调度到系统线程上执行。

可以把 goroutine 理解成 Go 提供的轻量任务。相比直接创建系统线程，goroutine 创建成本更低，调度由 Go runtime 负责。

## 基本写法

```go
go func() {
    fmt.Println("running")
}()
```

在函数调用前加 `go`，这个函数就会在新的 goroutine 中执行。

## 和线程的区别

线程由操作系统调度，goroutine 由 Go runtime 调度。多个 goroutine 可以复用较少数量的系统线程。

goroutine 更轻量，但并不意味着可以无节制创建。大量 goroutine 如果阻塞或泄漏，也会造成内存和调度压力。

## 主函数结束问题

```go
func main() {
    go fmt.Println("hello")
}
```

这段代码可能看不到输出，因为 `main` 函数结束后，程序会直接退出，其他 goroutine 也会结束。

通常需要使用 `sync.WaitGroup`、channel 或其他同步方式等待 goroutine 完成。

## 使用 WaitGroup 等待

```go
var wg sync.WaitGroup
wg.Add(1)

go func() {
    defer wg.Done()
    fmt.Println("running")
}()

wg.Wait()
```

`WaitGroup` 用来等待一组 goroutine 执行完成。

## goroutine 和 channel

goroutine 负责并发执行，channel 负责 goroutine 之间通信。

```go
ch := make(chan int)

go func() {
    ch <- 1
}()

value := <-ch
```

channel 可以传递数据，也可以用于同步。

## 常见误区

第一个误区是把 goroutine 等同于线程。goroutine 是 Go runtime 调度的任务，不是直接的系统线程。

第二个误区是认为 `go` 关键字一定会让代码执行完。主函数结束、上下文取消或 goroutine 阻塞时，都可能导致任务没有按预期完成。

第三个误区是忽略 goroutine 泄漏。如果 goroutine 一直阻塞在 channel 或网络请求上，它就可能长期存在。

## 适用场景

goroutine 适合处理并发任务，例如并发请求、后台任务、流水线处理和生产者消费者模型。
