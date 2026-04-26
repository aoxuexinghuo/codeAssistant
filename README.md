# 基于大模型的编程答疑助手

面向编程学习场景的教学型答疑系统。项目以“大模型答疑 + 本地知识库 RAG + 薄弱点沉淀”为主线，帮助用户完成从提问、理解、复盘到资料补齐的学习闭环。

## 核心闭环

```text
学习中心浏览资料
→ 智能答疑提问
→ RAG 检索本地知识库增强回答
→ 自动沉淀薄弱点卡片
→ 回到学习中心复习资料
```

当前系统已经把学习中心和 RAG 知识库打通：二者都使用 `backend/knowledge` 下的 Markdown 文件。

## 已实现功能

- 多模式答疑：调试模式、学习模式、面试模式。
- 流式输出：普通答疑和 RAG 知识库增强答疑均支持 SSE 流式返回。
- Markdown 渲染：助手回答、会话历史和学习资料详情支持 Markdown。
- 会话历史：支持查询、清空、删除单条历史、复用历史问题。
- 学习中心：读取本地 Markdown 知识库，按主题展示资料卡片和详情页。
- RAG 知识库增强：检索本地 Markdown 片段，生成回答并展示参考来源。
- 薄弱点卡片：支持自动沉淀、手动新增、编辑、删除、拖拽排序、搜索和筛选。
- 登录注册页面：目前为前端原型，可后续接入真实用户体系。

## 技术栈

### 前端

- `Vue 3`
- `Vue Router`
- `Vite`
- `fetch`
- `SSE`
- `marked`
- `DOMPurify`

### 后端

- `Python`
- `Flask`
- `Flask-SQLAlchemy`
- `SQLite`
- `LangChain`
- `langchain-openai`
- OpenAI-compatible 模型接口

## 项目结构

```text
.
├─ backend
│  ├─ app
│  │  ├─ services
│  │  │  ├─ embedding_service.py     # 轻量检索分词，占位 Embedding 层
│  │  │  ├─ history_service.py       # 会话历史
│  │  │  ├─ knowledge_service.py     # 本地 Markdown 知识库读取
│  │  │  ├─ llm_service.py           # LangChain 模型调用
│  │  │  ├─ mistake_service.py       # 薄弱点卡片
│  │  │  ├─ mode_service.py          # 答疑模式配置
│  │  │  ├─ prompt_service.py        # 提示词
│  │  │  ├─ rag_service.py           # RAG 编排
│  │  │  └─ retriever_service.py     # 本地检索
│  │  ├─ __init__.py                 # Flask 应用工厂
│  │  ├─ config.py                   # 配置
│  │  ├─ extensions.py               # Flask 扩展
│  │  ├─ models.py                   # SQLAlchemy 模型
│  │  └─ routes.py                   # API 路由
│  ├─ data
│  │  ├─ programming_assistant.db    # SQLite 数据库
│  │  └─ rag_index.json              # RAG 本地索引
│  ├─ knowledge                      # 本地 Markdown 知识库
│  ├─ requirements.txt
│  ├─ package.json
│  └─ server.py
├─ frontend
│  ├─ src
│  │  ├─ components
│  │  ├─ data
│  │  ├─ router
│  │  ├─ services
│  │  ├─ views
│  │  ├─ App.vue
│  │  ├─ main.js
│  │  └─ style.css
│  ├─ package.json
│  └─ vite.config.js
├─ package.json
└─ README.md
```

说明：

- 当前前端入口是 `frontend/src`。
- 当前后端入口是 `backend/server.py`。
- 根目录旧的 `src`、`dist` 不是当前主要开发入口。

## 环境要求

### Node.js

建议：

```text
Node.js >= 20.19.0
```

如果版本较低，Vite 构建时会出现版本警告。

### Python

建议：

```text
Python >= 3.10
```

当前项目在 Python 3.12 环境下验证过。

## 安装依赖

在项目根目录执行：

```bash
npm install
python -m pip install -r backend/requirements.txt
```

如果只安装前端依赖：

```bash
npm --prefix frontend install
```

## 模型配置

后端使用 `LangChain` 的 `ChatOpenAI` 接入 OpenAI-compatible 模型服务。

PowerShell 示例：

```powershell
$env:DASHSCOPE_API_KEY="你的 API Key"
$env:LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qvq-max-2025-03-25"
```

可选配置：

```powershell
$env:LLM_TEMPERATURE="0.7"
$env:LLM_MAX_TOKENS="1200"
$env:DATABASE_URL="sqlite:///backend/data/programming_assistant.db"
$env:RAG_TOP_K="3"
$env:RAG_MIN_SCORE="0.25"
$env:RAG_CHUNK_SIZE="500"
$env:RAG_CHUNK_OVERLAP="80"
```

说明：

- `LLM_API_KEY` 和 `DASHSCOPE_API_KEY` 二选一即可。
- `LLM_BASE_URL` 填写兼容 OpenAI 协议的模型服务地址。
- `LLM_MODEL` 填写当前账号可用的模型名称。
- 后端启动时会自动重建 RAG 索引。

## 启动项目

### 1. 启动后端

```bash
npm run dev:backend
```

默认地址：

```text
http://localhost:3000
```

健康检查：

```text
http://localhost:3000/api/health
```

### 2. 启动前端

新开一个终端：

```bash
npm run dev:frontend
```

默认地址：

```text
http://localhost:5173
```

### 3. 访问页面

```text
http://localhost:5173
```

前端通过 Vite 代理访问后端 `/api`，代理配置位于：

```text
frontend/vite.config.js
```

## 常用命令

```bash
npm run dev:backend       # 启动 Flask 后端
npm run dev:frontend      # 启动 Vue 前端
npm run build             # 构建前端
npm run build:frontend    # 构建前端
npm run start:backend     # 启动后端
python -m compileall backend/app
```

## 页面说明

### 首页

项目入口页，展示主要学习流程入口：

- 智能答疑
- 薄弱点记录
- 学习中心

### 智能答疑

核心问答页面。

支持：

- 调试 / 学习 / 面试三种模式。
- 普通流式问答。
- 知识库增强流式问答。
- 自动沉淀薄弱点开关。
- 会话历史弹窗。
- RAG 参考来源展示。

### 学习中心

学习中心读取：

```text
backend/knowledge/*.md
```

并展示为资料卡片。点击卡片后进入 Markdown 详情页。

这批资料同时用于 RAG 检索。

### 薄弱点

用于复盘学习过程中暴露出的知识点。

支持：

- 自动生成
- 手动新增
- 编辑修改
- 删除
- 拖拽排序
- 搜索
- 按主题筛选
- 按类型筛选

### 登录注册

目前是前端原型页面，默认提交后进入系统主页。后续可接入真实用户注册、登录和鉴权。

## 知识库资料

当前内置 Markdown 资料：

```text
backend/knowledge/algorithm-complexity.md
backend/knowledge/c-pointer.md
backend/knowledge/c-struct.md
backend/knowledge/go-channel.md
backend/knowledge/go-goroutine.md
backend/knowledge/java-collections.md
backend/knowledge/java-oop.md
backend/knowledge/python-basics.md
backend/knowledge/rust-ownership.md
backend/knowledge/rust-result.md
backend/knowledge/vue-components.md
backend/knowledge/vue-reactivity.md
```

修改这些 Markdown 后，重启后端即可自动重建索引。

## RAG 机制

当前 RAG 是第一版轻量实现，流程如下：

```text
读取 backend/knowledge Markdown
→ 清洗和切分文本
→ 生成本地 rag_index.json
→ 用户提问
→ 关键词检索 top_k 片段
→ 过滤低相关片段
→ 拼接上下文
→ 调用大模型
→ 返回回答和参考来源
```

当前 RAG 特点：

- 使用本地 Markdown 作为知识库。
- 后端启动时自动重建索引。
- 支持普通 RAG 回答和 RAG 流式回答。
- 默认 `RAG_TOP_K=3`。
- 默认 `RAG_MIN_SCORE=0.25`。
- 后端控制台输出 `[rag] hit` 或 `[rag] no hit` 日志。

后续可以将 `retriever_service.py` 替换为 `Chroma` 或 `FAISS` 向量检索。

## 提示词策略

为了避免回答过长，当前答疑提示词默认要求：

- 不写成长篇教程。
- 默认控制在约 120 字以内。
- 列表最多 3 条。
- 代码最多 8 行。
- 用户未明确要求详细解释时，不主动展开完整知识体系。

如果需要更详细回答，可以明确输入：

```text
请详细解释
请给完整代码
请展开讲
```

## API 概览

### 基础

```text
GET /api/health
GET /api/modes
```

### 知识库

```text
GET /api/knowledge
GET /api/knowledge/<file>
```

### 普通答疑

```text
POST /api/assistant/reply
POST /api/assistant/reply-stream
```

### RAG

```text
POST /api/rag/rebuild
POST /api/rag/reply
POST /api/rag/reply-stream
```

### 会话历史

```text
GET /api/history
POST /api/history
DELETE /api/history
DELETE /api/history/<id>
```

### 薄弱点

```text
GET /api/mistakes
POST /api/mistakes
PUT /api/mistakes/<id>
DELETE /api/mistakes/<id>
POST /api/mistakes/from-assistant
POST /api/mistakes/<id>/move
POST /api/mistakes/reorder
```

## 后续扩展方向

### 1. Chroma + Embedding

当前 RAG 使用轻量关键词检索。后续可升级为：

```text
Markdown
→ Embedding
→ Chroma / FAISS
→ 语义检索
→ RAG 回答
```

这样能提升同义问题和语义相近问题的检索效果。

### 2. 薄弱点关联资料来源

后续可以把 RAG 命中的资料来源保存到薄弱点卡片中，让卡片直接跳转到推荐复习资料。

### 3. 用户体系

登录注册页目前是前端原型。后续可增加：

- 用户注册
- 用户登录
- Token 鉴权
- 历史记录按用户隔离
- 薄弱点按用户隔离

### 4. Agent

后续可以将系统升级为编程学习 Agent，让模型根据任务自动选择工具：

- 查询知识库
- 查询历史会话
- 查询薄弱点
- 新增薄弱点
- 生成答疑回答

## 常见问题

### 前端接口失败

先确认后端是否启动：

```text
http://localhost:3000/api/health
```

### 模型接口调用失败

检查环境变量：

```powershell
echo $env:DASHSCOPE_API_KEY
echo $env:LLM_BASE_URL
echo $env:LLM_MODEL
```

并确认 API Key 支持当前模型和调用方式。

### RAG 没有引用来源

可能原因：

- 问题和知识库资料相关度不足。
- `RAG_MIN_SCORE` 阈值过高。
- Markdown 修改后后端还没有重启。

### 自动沉淀薄弱点没有出现

检查：

- 答疑页“自动沉淀薄弱点”是否开启。
- 问题是否属于明确的编程学习问题。
- 后端控制台是否有 `[mistake-extraction]` 日志。

### 前端构建提示 Node 版本

如果看到：

```text
Vite requires Node.js version 20.19+ or 22.12+
```

建议升级 Node.js 到 `20.19+` 或 `22.12+`。
