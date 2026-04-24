# Java 集合

## 核心概念

Java 集合用于保存和操作一组对象。常见集合包括 `List`、`Set` 和 `Map`。

不同集合的重点不同：`List` 关注顺序，`Set` 关注不重复，`Map` 关注键值对应关系。

## List

`List` 是有序集合，允许重复元素。

```java
List<String> names = new ArrayList<>();
names.add("Tom");
names.add("Jerry");
```

常见实现有 `ArrayList` 和 `LinkedList`。

## Set

`Set` 不允许重复元素。

```java
Set<String> tags = new HashSet<>();
tags.add("Java");
tags.add("Java");
```

最终集合里只会保留一个 `"Java"`。

## Map

`Map` 保存键值对。

```java
Map<String, Integer> scores = new HashMap<>();
scores.put("Tom", 90);
```

通过 key 可以快速找到对应 value。

## 泛型

泛型用于限制集合中元素的类型。

```java
List<Integer> numbers = new ArrayList<>();
```

这样可以避免把错误类型的元素放进集合。

## 遍历集合

```java
for (String name : names) {
    System.out.println(name);
}
```

增强 for 循环适合遍历集合。

## ArrayList 和 LinkedList

`ArrayList` 底层更接近动态数组，随机访问快。

`LinkedList` 底层是链表结构，插入和删除节点更灵活，但随机访问较慢。

大多数普通场景优先使用 `ArrayList`。

## HashMap 常见点

`HashMap` 根据 key 计算位置，适合快速查找。

key 需要正确实现 `equals` 和 `hashCode`，否则可能出现查找异常。

## 常见误区

第一个误区是用 `List` 去做频繁查找和去重，这时 `Set` 或 `Map` 可能更合适。

第二个误区是忽略泛型，导致集合里混入错误类型。

第三个误区是认为所有集合都是线程安全的。常见的 `ArrayList`、`HashMap` 默认都不是线程安全集合。
