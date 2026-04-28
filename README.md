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
- 会话历史：支持按登录用户隔离、查询、清空、删除单条历史、复用历史问题。
- 学习档案：独立页面展示基础偏好、能力能量环、方向气泡图、薄弱点标签云和个性化策略。
- 学习中心：读取系统 Markdown 知识库，也支持登录用户上传个人 Markdown 资料。
- RAG 知识库增强：检索本地 Markdown 片段，生成回答并展示参考来源。
- 薄弱点卡片：支持按登录用户隔离、自动沉淀、手动新增、编辑、删除、拖拽排序、搜索和筛选。
- 登录注册：支持轻量账号注册和登录，前端使用本地 token 识别当前用户。

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
- `Chroma`
- `Embedding`
- `OpenAI-compatible` 模型接口

## 项目结构

```text
.
├─ backend
│  ├─ app
│  │  ├─ services
│  │  │  ├─ embedding_service.py     # 关键词检索分词
│  │  │  ├─ history_service.py       # 会话历史
│  │  │  ├─ knowledge_chunk_service.py # 知识库清洗与切片
│  │  │  ├─ knowledge_service.py     # 本地 Markdown 知识库读取
│  │  │  ├─ llm_service.py           # LangChain 模型调用
│  │  │  ├─ markdown_service.py      # Markdown 元数据解析
│  │  │  ├─ mistake_service.py       # 薄弱点卡片
│  │  │  ├─ mode_service.py          # 答疑模式配置
│  │  │  ├─ prompt_service.py        # 提示词
│  │  │  ├─ profile_service.py       # 用户画像与学习状态统计
│  │  │  ├─ rag_service.py           # RAG 编排
│  │  │  ├─ retriever_service.py     # 检索入口与关键词兜底
│  │  │  └─ vector_store_service.py  # Chroma 向量检索
│  │  ├─ __init__.py                 # Flask 应用工厂
│  │  ├─ config.py                   # 配置
│  │  ├─ extensions.py               # Flask 扩展
│  │  ├─ models.py                   # SQLAlchemy 模型
│  │  └─ routes.py                   # API 路由
│  ├─ data
│  │  ├─ programming_assistant.db    # SQLite 数据库
│  │  └─ rag_index.json              # 关键词检索兜底索引
│  ├─ knowledge                      # 本地 Markdown 知识库
│  ├─ vector_store                   # Chroma 向量库
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

### 基础聊天模型配置

PowerShell 示例：

```powershell
$env:DASHSCOPE_API_KEY="你的 API Key"
$env:LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qvq-max-2025-03-25"
```

### API Key 关系

项目中有三个和模型调用有关的 Key 配置：

```text
DASHSCOPE_API_KEY   阿里云百炼平台的 API Key
LLM_API_KEY         聊天模型调用使用的 Key
EMBEDDING_API_KEY   Embedding 向量模型调用使用的 Key
```

它们不是三种必须分别申请的 Key。通常情况下，如果聊天模型和 Embedding 模型都使用阿里云百炼，可以只配置：

```powershell
$env:DASHSCOPE_API_KEY="你的百炼 API Key"
```

项目会按下面的优先级读取 Embedding Key：

```text
EMBEDDING_API_KEY
→ LLM_API_KEY
→ DASHSCOPE_API_KEY
```

也就是说，`EMBEDDING_API_KEY` 只是项目里给“向量化资料”这一步单独预留的配置名。大多数情况下可以直接复用 `DASHSCOPE_API_KEY`。

只有在下面这种情况，才需要单独设置 `EMBEDDING_API_KEY`：

```text
聊天模型使用一个平台或账号
Embedding 模型使用另一个平台或账号
```

示例：

```powershell
$env:EMBEDDING_API_KEY="你的 Embedding 服务 Key"
$env:EMBEDDING_BASE_URL="Embedding 服务的 OpenAI-compatible 地址"
$env:EMBEDDING_MODEL="对应的 Embedding 模型名"
```

### 向量检索配置

如果复用阿里云百炼的 Key，可以这样配置：

```powershell
$env:DASHSCOPE_API_KEY="你的百炼 API Key"
$env:LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qvq-max-2025-03-25"

$env:RAG_RETRIEVER_TYPE="vector"
$env:EMBEDDING_MODEL="text-embedding-v4"
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
$env:RAG_RETRIEVER_TYPE="vector"
$env:EMBEDDING_MODEL="text-embedding-v4"
```

说明：

- `LLM_API_KEY` 和 `DASHSCOPE_API_KEY` 二选一即可；使用阿里云百炼时通常只配置 `DASHSCOPE_API_KEY`。
- `LLM_BASE_URL` 填写兼容 OpenAI 协议的模型服务地址。
- `LLM_MODEL` 填写当前账号可用的模型名称。
- `RAG_RETRIEVER_TYPE=vector` 使用 Chroma 向量检索；设置为 `keyword` 可切回关键词检索。
- `EMBEDDING_API_KEY`、`EMBEDDING_BASE_URL` 可单独配置；不配置时默认复用 `LLM_API_KEY` 或 `DASHSCOPE_API_KEY`。
- `EMBEDDING_MODEL` 需要填写当前账号支持的 Embedding 模型。
- 后端启动时会自动重建 RAG 索引。

注意：向量检索在重建 Chroma 索引时会把 `backend/knowledge` 中的资料内容发送给 Embedding 服务生成向量。如果资料包含隐私内容，请先确认所使用的 Embedding 服务是否可信，或将 `RAG_RETRIEVER_TYPE` 设置为 `keyword`。

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
backend/user_knowledge/user_<用户ID>/*.md
```

并展示为资料卡片。点击卡片后进入 Markdown 详情页。

学习中心只保留“上传个人资料”的入口，上传表单位于二级页面：

```text
/learning/upload
```

个人资料只对当前登录用户可见，并会进入该用户的 RAG 检索范围。

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

支持轻量账号注册和登录。登录成功后前端会保存用户 token，并在后续接口请求中自动带上 `X-User-Token`。

当前已按用户隔离：

- 学习档案
- 会话历史
- 薄弱点
- 个人上传资料

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

当前 RAG 已支持 `Chroma + Embedding` 向量检索，并保留关键词检索作为兜底。

```text
读取 backend/knowledge Markdown
→ 清洗和切分文本
→ 调用 Embedding 模型生成向量
→ 写入 Chroma 本地向量库
→ 用户提问
→ 问题向量化
→ 语义检索 top_k 片段
→ 过滤低相关片段
→ 拼接上下文
→ 调用大模型
→ 返回回答和参考来源
```

当前 RAG 特点：

- 使用本地 Markdown 作为知识库。
- 后端启动时自动重建关键词索引和 Chroma 向量库。
- 支持普通 RAG 回答和 RAG 流式回答。
- 支持 `/api/rag/search` 查看实际命中的资料片段和分数。
- 默认 `RAG_TOP_K=3`。
- 默认 `RAG_MIN_SCORE=0.25`。
- 后端控制台输出 `[rag] hit` 或 `[rag] no hit` 日志。
- 如果 Chroma、Embedding 配置或依赖不可用，会自动回退到关键词检索。

如果暂时不想调用外部 Embedding 服务，可以使用：

```powershell
$env:RAG_RETRIEVER_TYPE="keyword"
```

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

## 学习档案

当前学习档案是用户画像的初版实现，采用“手动基础画像 + 自动行为画像”的方式。

页面入口：

```text
/profile
```

左侧导航中显示为“学习档案”。

手动画像包括：

```text
昵称
编程水平
学习方向
学习目标
回答偏好
薄弱点记录偏好
```

自动行为画像来自：

```text
会话历史
薄弱点卡片
模式使用记录
```

系统会据此生成：

```text
学习方向分布
能力概览
最近薄弱点
个性化策略
```

前端展示形式：

```text
能力能量环
方向气泡图
薄弱点标签云
策略便签卡片
```

画像会影响普通答疑和 RAG 答疑的提示词。例如：

```text
编程水平：初级
学习方向：C语言
回答偏好：多举例
```

系统会在回答时更偏向基础解释、C 语言语境和最小示例。

如果薄弱点记录偏好设置为“手动记录”，答疑页的“自动沉淀薄弱点”开关会默认关闭。

## API 概览

### 基础

```text
GET /api/health
GET /api/modes
```

### 学习档案

```text
GET /api/profile
PUT /api/profile
POST /api/profile/reset
GET /api/profile/insights
```

### 知识库

```text
GET /api/knowledge
POST /api/knowledge
GET /api/knowledge/<file>
```

`POST /api/knowledge` 用于上传当前登录用户的个人 Markdown 资料，资料会保存在：

```text
backend/user_knowledge/user_<用户ID>/
```

用户上传的资料只会出现在该用户的学习中心和 RAG 检索中。

### 登录注册

```text
POST /api/auth/register
POST /api/auth/login
```

登录成功后前端会保存 `token`，后续请求通过请求头传递：

```text
X-User-Token: <token>
```

当前已按用户隔离：

```text
学习档案
会话历史
薄弱点
个人上传资料
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

### 1. 优化向量检索质量

当前已经接入 `Chroma + Embedding`，后续可以继续优化：

- 调整 chunk 大小和 overlap。
- 对不同 topic 使用不同检索阈值。
- 增加 rerank 重排模型。
- 增加混合检索：关键词召回 + 向量召回。

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
