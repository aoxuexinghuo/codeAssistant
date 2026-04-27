---
title: Java 面向对象
topic: Java
level: beginner
tags: [面向对象, 类, 对象, 封装, 继承, 多态]
---

# Java 面向对象

## 核心概念

Java 是典型的面向对象语言。面向对象的核心是把数据和行为组织到类中，再通过对象使用这些能力。

类是模板，对象是根据模板创建出来的具体实例。

## 类和对象

```java
class Student {
    String name;
    int age;

    void sayHello() {
        System.out.println("hello");
    }
}

Student s = new Student();
```

`Student` 是类，`s` 是对象。

## 成员变量和方法

成员变量描述对象的状态，方法描述对象能做什么。

```java
s.name = "Tom";
s.sayHello();
```

访问对象成员使用点运算符 `.`。

## 构造方法

构造方法用于创建对象时初始化数据。

```java
class Student {
    String name;

    Student(String name) {
        this.name = name;
    }
}
```

`this` 表示当前对象。

## 封装

封装是把对象内部数据保护起来，通过方法对外提供访问入口。

```java
class User {
    private String name;

    public String getName() {
        return name;
    }
}
```

`private` 可以限制外部直接访问字段。

## 继承

继承用于复用父类的属性和方法。

```java
class Dog extends Animal {
}
```

子类可以拥有父类能力，也可以扩展自己的能力。

## 多态

多态指同一个父类引用可以指向不同子类对象。

```java
Animal a = new Dog();
```

多态常用于降低代码耦合，让程序更容易扩展。

## 常见误区

第一个误区是把类和对象混为一谈。类是定义，对象才是真正被创建出来的数据。

第二个误区是滥用继承。不是所有复用都应该用继承，很多时候组合更清晰。

第三个误区是字段全部 public。这样会破坏封装，使对象状态难以维护。
