# Vue 3 响应式

## 核心概念

Vue 3 的响应式系统用于追踪状态变化，并在状态变化后更新页面。常用 API 包括 `ref`、`reactive`、`computed`、`watch` 和 `watchEffect`。

## ref

`ref` 适合包装基本类型或单个值。

```js
const count = ref(0)
count.value++
```

在 `<script setup>` 中访问和修改 `ref` 通常需要 `.value`。在模板中使用时，Vue 会自动解包。

## reactive

`reactive` 适合对象状态，会返回一个响应式代理对象。

```js
const state = reactive({
  name: 'Tom',
  age: 18,
})
```

访问对象属性时直接使用 `state.name`。

## ref 和 reactive 的区别

`ref` 可以包装基本类型，也可以包装对象；`reactive` 主要用于对象。

如果状态是一个简单值，例如数字、字符串、布尔值，优先使用 `ref`。

如果状态是一个整体对象，例如表单对象、配置对象，可以使用 `reactive`。

## 解构 reactive 的问题

直接解构 `reactive` 对象可能丢失响应式连接。

```js
const state = reactive({ count: 0 })
const { count } = state
```

如果需要解构并保留响应式，可以使用 `toRefs`。

## computed

`computed` 用于声明依赖响应式状态的派生值。

```js
const double = computed(() => count.value * 2)
```

当依赖变化时，计算结果会自动更新。

## watch

`watch` 适合监听明确的数据源。

```js
watch(count, (newValue, oldValue) => {
  console.log(newValue, oldValue)
})
```

它适合处理异步请求、日志记录、复杂副作用等场景。

## watchEffect

`watchEffect` 会自动收集函数执行过程中访问到的响应式依赖。

```js
watchEffect(() => {
  console.log(count.value)
})
```

它适合快速建立和响应式状态相关的副作用。

## watch 和 watchEffect 的区别

`watch` 的依赖来源明确，适合精确控制。

`watchEffect` 自动收集依赖，写法更简洁，但依赖不如 `watch` 直观。

## 常见误区

第一个误区是忘记在脚本中使用 `.value` 访问 `ref`。

第二个误区是直接解构 `reactive` 对象，导致响应式丢失。

第三个误区是把 `watchEffect` 当成所有场景的替代品。需要明确监听来源时，`watch` 更合适。
