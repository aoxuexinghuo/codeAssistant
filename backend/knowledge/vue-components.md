---
title: Vue 3 组件通信
topic: Vue 3
level: beginner
tags: [组件通信, props, emit, v-model, provide, inject]
---

# Vue 3 组件通信

## 核心概念

组件通信是指不同组件之间传递数据和触发行为。Vue 3 常见通信方式包括 props、emit、provide/inject 和状态管理。

选择通信方式时，先看组件关系：父子组件、跨层组件，还是多个无直接关系的组件。

## 父传子 props

父组件通过 props 把数据传给子组件。

```vue
<UserCard :name="username" />
```

子组件声明 props：

```js
defineProps({
  name: String,
})
```

props 是父组件传入的数据，子组件不应该直接修改 props。

## 子传父 emit

子组件通过 emit 通知父组件发生了某个事件。

```js
const emit = defineEmits(['save'])
emit('save', form)
```

父组件监听事件：

```vue
<EditForm @save="handleSave" />
```

## v-model 组件通信

自定义组件可以通过 `v-model` 实现双向绑定。

```vue
<SearchBox v-model="keyword" />
```

子组件通常接收 `modelValue`，并触发 `update:modelValue`。

## provide 和 inject

`provide/inject` 适合跨层传递数据。

```js
provide('theme', theme)
```

后代组件可以注入：

```js
const theme = inject('theme')
```

它适合主题、配置、上下文等跨层数据。

## 状态管理

当多个无直接关系的组件需要共享状态时，可以使用状态管理方案，例如 Pinia。

状态管理适合用户信息、权限、购物车、全局配置等场景。

## 常见误区

第一个误区是子组件直接修改 props。正确方式是 emit 通知父组件修改。

第二个误区是所有通信都用 provide/inject。简单父子通信优先 props 和 emit。

第三个误区是过早引入全局状态管理。只有多个页面或多个组件共享复杂状态时才需要。
