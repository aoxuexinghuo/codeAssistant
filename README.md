# 基于大模型的编程答疑助手

一个面向教学场景的编程答疑项目，当前提供三种问答模式：

- `调试模式`：先补齐上下文，再给排查步骤
- `学习模式`：强调概念解释、原理拆解和简短示例
- `面试模式`：优先给思路、关键词和答题框架

项目采用前后端分离结构：

- 前端：`Vue 3 + Vite`
- 后端：`Flask + LangChain`

## 技术栈

### 前端

- `Vue 3`
- `Vue Router`
- `Vite`
- 原生 `fetch`
- `SSE` 流式展示问答结果

### 后端

- `Python 3.12+`
- `Flask`
- `LangChain`
- `langchain-openai`
- OpenAI-compatible 模型接口

### 当前模型接入方式

后端通过 `LangChain` 的 `ChatOpenAI` 接入兼容 OpenAI 协议的模型平台，例如：

- 阿里云百炼
- 硅基流动
- 火山方舟
- 其他 OpenAI-compatible 平台

## 当前项目结构

```text
.
├─ backend
│  ├─ app
│  │  ├─ services
│  │  │  ├─ history_service.py
│  │  │  ├─ llm_service.py
│  │  │  ├─ mode_service.py
│  │  │  └─ prompt_service.py
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  └─ routes.py
│  ├─ requirements.txt
│  ├─ package.json
│  └─ server.py
├─ frontend
│  ├─ src
│  │  ├─ components
│  │  ├─ router
│  │  ├─ services
│  │  ├─ views
│  │  ├─ App.vue
│  │  ├─ main.js
│  │  └─ style.css
│  ├─ vite.config.js
│  └─ package.json
├─ package.json
└─ README.md
```

## 目录职责

### `frontend/src/views`

页面容器层，负责页面状态和页面编排。

### `frontend/src/components`

展示组件层，负责页面模块和交互表现。

### `frontend/src/services`

前端接口访问层，统一封装 `/api` 请求。

### `backend/app/routes.py`

后端接口入口，定义 Flask 路由。

### `backend/app/services`

后端业务层：

- `mode_service.py`：模式配置和兜底回复
- `prompt_service.py`：提示词构造
- `llm_service.py`：LangChain 模型调用
- `history_service.py`：会话历史

## 已实现功能

- 登录 / 注册页面原型
- 智能答疑页面
- `调试 / 学习 / 面试` 三种模式切换
- 流式问答输出
- 会话历史记录
- 学习中心页面
- 错题本页面
- 学习资料详情页

## 环境要求

### Node.js

建议：

- `Node.js >= 20.19.0`

当前前端使用 `Vite`，如果版本过低，构建时可能会出现兼容性提示。

### Python

建议：

- `Python >= 3.10`

当前已在 `Python 3.12` 环境下验证。

## 安装依赖

### 前端依赖

在项目根目录执行：

```bash
npm install
npm --prefix frontend install
```

### 后端依赖

如果本机还没有安装 Python 依赖，执行：

```bash
python -m pip install -r backend/requirements.txt
```

## 模型环境变量配置

启动后端前，需要在当前终端中配置模型环境变量。

PowerShell 示例：

```powershell
$env:DASHSCOPE_API_KEY="你的 API Key"
$env:LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qvq-max-2025-03-25"
```

可选参数：

```powershell
$env:LLM_TEMPERATURE="0.7"
$env:LLM_MAX_TOKENS="1200"
```

说明：

- 后端同时支持 `LLM_API_KEY` 和 `DASHSCOPE_API_KEY`
- `LLM_BASE_URL` 需要填写兼容 OpenAI 协议的基础地址
- 后端模型调用现在由 `Flask + LangChain` 承载

## 启动项目

### 1. 启动后端

在项目根目录执行：

```bash
npm run dev:backend
```

默认地址：

```text
http://localhost:3000
```

### 2. 启动前端

新开一个终端，在项目根目录执行：

```bash
npm run dev:frontend
```

默认地址：

```text
http://localhost:5173
```

### 3. 打开页面

浏览器访问：

```text
http://localhost:5173
```

前端代理配置在 `frontend/vite.config.js`：

```js
proxy: {
  '/api': 'http://localhost:3000',
}
```

这意味着前端访问 `/api/...` 时，会自动转发到 Flask 后端。

## 常用命令

```bash
npm run dev:backend
npm run dev:frontend
npm run build
npm run build:frontend
npm run start:backend
```

## 主要接口

### `GET /api/health`

健康检查接口。

### `GET /api/modes`

获取三种问答模式配置。

### `POST /api/assistant/reply`

普通问答接口，返回完整回复。

请求示例：

```json
{
  "mode": "learning",
  "question": "帮我解释一下 Vue 3 的 ref 和 reactive 区别"
}
```

### `POST /api/assistant/reply-stream`

流式问答接口，前端当前优先使用这条接口。

### `GET /api/history`

获取当前运行期内的会话历史。

### `POST /api/history`

新增一条会话历史记录。

### `DELETE /api/history`

清空当前运行期内的会话历史。

## 后端后续技术路线建议

你现在计划的方向是：

- `Flask + LangChain + RAG`

这个方向是合理的，适合作为毕设主线。建议你把后端继续拆成下面几层：

### 1. Web 层

使用 `Flask` 负责：

- 路由
- 请求参数校验
- 响应格式
- SSE 流式输出
- 用户会话

### 2. Chain 层

使用 `LangChain` 负责：

- PromptTemplate
- ChatModel
- Retriever
- RAG chain
- 输出约束

### 3. Knowledge 层

单独维护知识库相关能力：

- 文档加载
- 文本切分
- 向量化
- 向量检索
- 引用片段返回

### 4. Persistence 层

单独维护持久化能力：

- 用户表
- 会话历史
- 学习记录
- 错题记录
- 资料索引

## 对后端的具体建议

如果你后续确定主打 `Flask + LangChain + RAG`，我建议再补这几个点：

### 1. 增加 `SQLAlchemy`

原因：

- 现在历史记录还是内存级
- 后面做用户、会话、错题本都需要数据库

推荐：

- `Flask + SQLAlchemy`
- 数据库先用 `SQLite`
- 后续再切 `MySQL` 或 `PostgreSQL`

### 2. 增加向量库或本地向量存储

RAG 必须要有检索层。

第一阶段推荐：

- `FAISS`
- 或 `Chroma`

原因：

- 本地开发简单
- 适合毕设演示
- 和 LangChain 集成成熟

### 3. 增加 Embedding 层

RAG 不只是“把资料喂给模型”，还要有向量化。

建议单独抽出：

- `embedding_service.py`
- `retriever_service.py`
- `rag_service.py`

### 4. 增加文档预处理

后面知识库如果来自：

- Markdown
- PDF
- 网页资料
- 课程讲义

建议单独做：

- 文档清洗
- 文本切分
- 元数据标记

否则后面 RAG 质量会不稳定。

### 5. 增加统一配置管理

现在已有 `config.py`，后面建议继续扩：

- 模型配置
- 数据库配置
- 向量库配置
- 检索参数配置

这样方便答辩时讲“系统具备可配置能力”。

### 6. 增加日志和异常处理

建议后面统一加入：

- 请求日志
- 模型调用日志
- 检索日志
- 错误日志

因为你做的是教学型系统，后面排查模型回复问题和 RAG 命中问题时会很有用。

## 推荐的后端演进顺序

建议按这个顺序推进：

1. 先把 `Flask + LangChain` 当前链路跑稳
2. 给历史记录接数据库
3. 引入 `FAISS` 或 `Chroma`
4. 接 Embedding
5. 做第一版 RAG
6. 给回答结果增加引用来源
7. 再补用户体系、学习记录和错题本持久化

## 当前最值得增加的后端技术点

如果你问“除了 `Flask + LangChain + RAG`，还建议什么”，我给你的答案是：

1. `SQLAlchemy`
2. `FAISS` 或 `Chroma`
3. `Embedding Service`
4. 日志系统
5. 配置管理

这五个点比一开始就上复杂 Agent 更实用，也更适合毕设叙述。
