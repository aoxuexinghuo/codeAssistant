# Go channel

## 核心概念

channel 是 Go 中用于 goroutine 之间通信的机制。goroutine 负责并发执行，channel 负责传递数据和同步状态。

可以把 channel 理解成一条管道：一端发送数据，另一端接收数据。

## 基本写法

```go
ch := make(chan int)
```

这会创建一个传递 `int` 类型数据的 channel。

## 发送和接收

```go
ch <- 1
value := <-ch
```

`ch <- 1` 表示向 channel 发送数据，`<-ch` 表示从 channel 接收数据。

## 和 goroutine 配合

```go
ch := make(chan int)

go func() {
    ch <- 100
}()

value := <-ch
```

接收操作会等待发送方发送数据，因此 channel 可以用于同步。

## 无缓冲 channel

无缓冲 channel 的发送和接收需要同时准备好，否则会阻塞。

```go
ch := make(chan int)
```

这种 channel 常用于严格同步。

## 有缓冲 channel

```go
ch := make(chan int, 2)
```

有缓冲 channel 可以先存放一定数量的数据，缓冲区满了才会阻塞发送。

## 关闭 channel

```go
close(ch)
```

关闭 channel 通常表示发送方不会再发送新数据。

接收方可以用 `range` 持续读取：

```go
for value := range ch {
    fmt.Println(value)
}
```

## select

`select` 可以同时等待多个 channel 操作。

```go
select {
case value := <-ch:
    fmt.Println(value)
case <-done:
    return
}
```

它常用于超时控制、取消任务和多路通信。

## 常见误区

第一个误区是忘记 channel 操作可能阻塞。没有接收方时，无缓冲 channel 发送会阻塞。

第二个误区是在接收方关闭 channel。通常应该由发送方关闭。

第三个误区是把 channel 当成全局队列滥用。channel 更适合表达 goroutine 之间明确的数据流和同步关系。
