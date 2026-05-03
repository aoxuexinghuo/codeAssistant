# 基于大模型的编程答疑助手

一个面向编程学习场景的教学型答疑系统。项目以“编程答疑”为核心，结合 RAG 知识库、薄弱点沉淀、AI 复盘、学习计划、任务积分和用户画像，帮助学习者从一次提问延伸到持续复盘和个性化学习。

当前项目已经拆分为 Vue 3 前端和 Flask 后端，后端使用 LangChain 调用 DeepSeek 等 OpenAI-compatible 大模型接口，并支持本地 Markdown 知识库检索。

## 功能总览

### 智能答疑

- 支持调试模式、学习模式、面试模式三种回答策略。
- 支持普通大模型流式输出。
- 支持 RAG 知识库增强流式输出。
- 支持 Markdown 回答渲染，包括代码块、列表和标题。
- 支持会话历史记录。
- 支持删除单条历史会话。
- 支持自动沉淀薄弱点开关。
- 支持显示薄弱点沉淀结果。
- 支持展示 RAG 命中的资料来源。
- RAG 来源可以跳转到知识库对应资料页。

### 知识库

- 支持系统内置 Markdown 学习资料。
- 支持当前用户上传个人 Markdown 资料。
- 上传个人资料采用知识库页内弹窗，不再单独跳转页面。
- 支持资料卡片浏览。
- 支持 Markdown 详情阅读。
- 支持删除当前用户上传的个人资料。
- 支持勾选多项资料生成学习计划。
- 支持关键词检索 RAG。
- 支持可选的 Chroma + Embedding 向量检索。

### 薄弱点记录

- 支持从答疑过程中自动提炼薄弱知识点。
- 支持手动新增薄弱点。
- 支持编辑薄弱点。
- 支持删除薄弱点。
- 支持拖拽调整顺序。
- 支持搜索和筛选。
- 支持复盘状态：待复盘、复盘中、已掌握。
- 支持 AI 生成复盘问题。
- 支持用户作答后由 AI 给出点评。
- 支持保存复盘内容。
- 支持标记掌握并获得复盘积分。
- 已掌握的薄弱点会在展示时降低优先级。

### 学习计划

- 支持在知识库中勾选资料生成学习计划。
- 支持结合用户画像、薄弱点和资料内容生成计划。
- 支持首页展示学习计划。
- 支持任务完成状态勾选。
- 每个任务有 1 到 5 分的积分。
- 首次完成任务时获得积分。
- 已获得积分的任务不会重复加分。
- 学习计划完成 100% 后可以生成阶段总结。
- 支持删除已有学习计划。

### 学习档案

- 展示学习等级。
- 展示升级进度。
- 展示累计积分。
- 展示提问数量、薄弱点数量、进行中任务和当前方向。
- 展示下一步建议。
- 展示薄弱点诊断。
- 展示近期关注方向。
- 展示个性化策略。
- 支持维护个人偏好。

### 登录注册与用户隔离

- 支持用户注册。
- 支持用户登录。
- 登录后前端保存用户 token。
- 后续请求通过 `X-User-Token` 识别当前用户。
- 会话历史按用户隔离。
- 薄弱点按用户隔离。
- 学习计划按用户隔离。
- 学习档案按用户隔离。
- 个人上传资料按用户隔离。

## 技术栈

### 前端

- Vue 3
- Vue Router
- Vite
- Fetch API
- Server-Sent Events，用于流式输出
- marked，用于 Markdown 渲染
- DOMPurify，用于清理 Markdown HTML
- 原生 CSS，自定义卡片式界面

### 后端

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- LangChain
- langchain-openai
- langchain-chroma
- Chroma
- DeepSeek API
- OpenAI-compatible Chat API

### 数据与检索

- SQLite：保存用户、会话历史、薄弱点、学习计划和用户画像。
- Markdown：保存系统知识库和用户上传资料。
- 关键词索引：默认 RAG 检索方式。
- Chroma：可选向量数据库。
- Embedding 服务：仅在启用向量检索时需要。

## 项目结构

```text
.
├─ backend
│  ├─ app
│  │  ├─ services
│  │  │  ├─ auth_service.py              # 登录注册、token 生成与用户查询
│  │  │  ├─ embedding_service.py         # Embedding 配置与客户端
│  │  │  ├─ history_service.py           # 会话历史增删查
│  │  │  ├─ knowledge_chunk_service.py   # 知识库文档切片
│  │  │  ├─ knowledge_service.py         # Markdown 资料读取、上传、删除
│  │  │  ├─ llm_service.py               # LangChain 大模型调用
│  │  │  ├─ markdown_service.py          # Markdown 元数据解析
│  │  │  ├─ mistake_service.py           # 薄弱点生成、编辑、复盘与积分
│  │  │  ├─ mode_service.py              # 答疑模式配置
│  │  │  ├─ profile_service.py           # 用户画像与学习档案
│  │  │  ├─ prompt_service.py            # 提示词构建
│  │  │  ├─ rag_service.py               # RAG 回答编排
│  │  │  ├─ retriever_service.py         # 检索入口
│  │  │  ├─ schema_service.py            # SQLite 轻量迁移
│  │  │  ├─ study_plan_service.py        # 学习计划生成与任务积分
│  │  │  └─ vector_store_service.py      # Chroma 向量库
│  │  ├─ __init__.py                     # Flask 应用工厂
│  │  ├─ config.py                       # 环境变量和目录配置
│  │  ├─ extensions.py                   # Flask 扩展实例
│  │  ├─ models.py                       # SQLAlchemy 数据模型
│  │  └─ routes.py                       # API 路由
│  ├─ data                               # SQLite 数据库和关键词索引
│  ├─ knowledge                          # 系统 Markdown 知识库
│  ├─ user_knowledge                     # 用户上传的个人资料
│  ├─ vector_store                       # Chroma 向量库目录
│  ├─ requirements.txt
│  ├─ package.json
│  └─ server.py
├─ frontend
│  ├─ src
│  │  ├─ components
│  │  │  ├─ assistant                    # 答疑页组件
│  │  │  ├─ auth                         # 登录注册组件
│  │  │  ├─ common                       # 通用组件
│  │  │  └─ layout                       # 全局布局
│  │  ├─ data                            # 前端静态数据
│  │  ├─ router                          # 路由配置
│  │  ├─ services                        # API 请求与页面状态
│  │  ├─ views                           # 页面视图
│  │  ├─ App.vue
│  │  ├─ main.js
│  │  └─ style.css
│  ├─ package.json
│  └─ vite.config.js
├─ package.json
└─ README.md
```

## 环境要求

建议版本：

```text
Node.js >= 20.19.0
Python >= 3.10
```

说明：

- Vite 7 推荐 Node.js `20.19+` 或 `22.12+`。
- 如果 Node 版本较低，前端构建可能出现版本警告。
- 后端当前使用 Python + Flask，不再使用 Node.js/Express 作为业务后端。

## 安装依赖

在项目根目录安装前端依赖：

```bash
npm install
```

安装后端 Python 依赖：

```bash
python -m pip install -r backend/requirements.txt
```

也可以只安装前端依赖：

```bash
npm --prefix frontend install
```

## 环境变量配置

### DeepSeek 最小配置

项目默认使用 DeepSeek 的 OpenAI-compatible 接口。

PowerShell 临时配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-v4-flash"
$env:RAG_RETRIEVER_TYPE="keyword"
```

然后在同一个 PowerShell 窗口启动后端：

```powershell
npm run dev:backend
```

PowerShell 永久配置：

```powershell
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "你的 DeepSeek API Key", "User")
[Environment]::SetEnvironmentVariable("LLM_BASE_URL", "https://api.deepseek.com", "User")
[Environment]::SetEnvironmentVariable("LLM_MODEL", "deepseek-v4-flash", "User")
[Environment]::SetEnvironmentVariable("RAG_RETRIEVER_TYPE", "keyword", "User")
```

永久配置后需要关闭当前终端，重新打开 PowerShell 后再启动项目。

### Key 读取优先级

后端读取大模型 Key 的优先级：

```text
LLM_API_KEY
→ DEEPSEEK_API_KEY
```

因此以下两种方式任选一种即可。

方式一：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

方式二：

```powershell
$env:LLM_API_KEY="你的 DeepSeek API Key"
```

如果两个都配置，优先使用 `LLM_API_KEY`。

### 常用可选配置

```powershell
$env:PORT="3000"
$env:DATABASE_URL="sqlite:///backend/data/programming_assistant.db"
$env:LLM_TEMPERATURE="0.7"
$env:LLM_MAX_TOKENS="1200"
$env:RAG_TOP_K="3"
$env:RAG_MIN_SCORE="0.25"
$env:RAG_CHUNK_SIZE="500"
$env:RAG_CHUNK_OVERLAP="80"
```

## 启动项目

### 1. 启动后端

```bash
npm run dev:backend
```

默认后端地址：

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

默认前端地址：

```text
http://localhost:5173
```

前端通过 Vite 代理访问后端 `/api`，代理配置在：

```text
frontend/vite.config.js
```

## 常用命令

```bash
npm run dev:backend       # 启动 Flask 后端
npm run dev:frontend      # 启动 Vue 前端
npm run build             # 构建前端
npm run build:frontend    # 构建前端
npm run start:backend     # 启动 Flask 后端
python -m compileall backend/app
```

## 页面说明

### 登录注册页

路由：

```text
/auth/login
/auth/register
```

功能：

- 用户注册。
- 用户登录。
- 登录成功后保存 token 和用户信息。
- 未登录也可以使用部分公共能力，但个人资料上传等能力需要登录。

前端本地保存：

```text
programming-assistant-token
programming-assistant-user
```

请求头：

```text
X-User-Token: <token>
```

### 首页

路由：

```text
/home
```

首页是学习任务执行入口。

主要模块：

- 今日薄弱点。
- 我的学习计划。
- 学习任务勾选。
- 任务积分反馈。
- 阶段总结入口。
- 智能答疑入口。
- 薄弱点记录入口。
- 知识库入口。

今日薄弱点逻辑：

- 优先展示今天新增的薄弱点。
- 如果今天没有新增，则展示最近待复盘的薄弱点。
- 已掌握的薄弱点优先级较低。

学习计划逻辑：

- 从知识库勾选资料后生成。
- 在首页执行计划。
- 勾选任务完成后获得对应积分。
- 计划完成 100% 后出现阶段总结入口。

### 智能答疑页

路由：

```text
/assistant
```

答疑模式：

```text
调试模式：先追问信息，再给排查步骤。
学习模式：解释概念，给必要例子和练习方向。
面试模式：偏提示和思路，不直接堆完整代码。
```

功能：

- 输入编程问题。
- 切换答疑模式。
- 选择普通答疑或 RAG 答疑。
- 流式输出回答。
- Markdown 格式渲染回答。
- 查看会话历史。
- 删除单条历史。
- 开关自动沉淀薄弱点。
- 显示薄弱点沉淀成功、无沉淀、失败三种状态。
- 显示 RAG 命中来源。

自动沉淀薄弱点的流程：

```text
用户提问
→ 大模型回答
→ 前端根据开关请求后端提炼薄弱点
→ 后端分析问题和回答
→ 生成 0 条或多条薄弱点卡片
→ 保存到当前用户账号
→ 前端显示沉淀结果
```

### 知识库页

路由：

```text
/learning
```

说明：页面名称已经改为“知识库”，但内部路由仍沿用旧的 `learning` 路径。

资料来源：

```text
backend/knowledge/*.md
backend/user_knowledge/user_<用户ID>/*.md
```

功能：

- 展示系统资料。
- 展示当前用户上传的个人资料。
- 按主题筛选资料。
- 查看资料详情。
- 勾选资料生成学习计划。
- 上传个人 Markdown 资料。
- 删除个人上传资料。

上传个人资料：

- 在知识库页点击“上传个人资料”。
- 页面会打开统一风格弹窗。
- 可以选择 Markdown 文件，也可以直接粘贴 Markdown 内容。
- 上传成功后资料进入当前用户的个人知识库。

兼容路由：

```text
/learning/upload
```

访问该路由时会自动回到知识库页并打开上传弹窗。

删除规则：

- 只能删除当前用户上传的个人资料。
- 系统内置资料不能删除。
- 删除后会重建 RAG 索引，避免继续命中已删除资料。

### 知识详情页

路由：

```text
/learning/<file>
```

功能：

- 查看 Markdown 资料内容。
- 渲染标题、段落、列表和代码块。
- 作为 RAG 来源跳转目标。

### 薄弱点记录页

路由：

```text
/mistakes
```

功能：

- 查看薄弱点卡片。
- 自动沉淀薄弱点。
- 手动新增薄弱点。
- 编辑薄弱点。
- 删除薄弱点。
- 拖拽排序。
- 搜索薄弱点。
- 按主题筛选。
- 按类型筛选。
- 打开 AI 复盘弹窗。

薄弱点卡片内容更偏知识点展示，不强制要求都有“我的答案、参考答案、错误原因、改进建议”四项。

AI 复盘流程：

```text
打开复盘
→ AI 生成一个针对该薄弱点的问题
→ 用户输入自己的回答
→ 可请求 AI 点评
→ 可保存复盘
→ 可标记掌握
→ 首次标记掌握获得 2 积分
```

复盘积分规则：

- 每条薄弱点首次标记掌握获得 2 分。
- 已获得复盘积分的薄弱点不会重复加分。
- 仅保存复盘或请求点评不会加分。

### 学习档案页

路由：

```text
/profile
```

学习档案用于展示个人学习状态和用户画像。

主要模块：

- 学习等级。
- 升级进度。
- 状态总览。
- 下一步建议。
- 薄弱点诊断。
- 近期关注方向。
- 个性化策略。
- 个人偏好设置。

学习等级来源：

- 学习计划任务积分。
- 薄弱点复盘积分。
- 当前用户的累计积分。

用户画像来源：

- 用户手动填写的偏好。
- 会话历史。
- 薄弱点记录。
- 当前学习计划。
- 常用答疑模式。

画像会影响：

- 普通答疑提示词。
- RAG 答疑提示词。
- 学习计划生成。
- 学习档案建议。

## RAG 说明

RAG 是 Retrieval-Augmented Generation，即“检索增强生成”。本项目中的作用是：先从本地知识库中找到和问题相关的资料片段，再把这些片段作为上下文交给大模型回答。

### 当前默认检索方式

默认使用关键词检索：

```powershell
$env:RAG_RETRIEVER_TYPE="keyword"
```

优点：

- 不需要额外 Embedding 服务。
- 不会把本地 Markdown 资料发送给向量化接口。
- 更适合当前本地资料量不大的阶段。

关键词 RAG 流程：

```text
读取 Markdown 资料
→ 解析元数据
→ 文本切片
→ 建立关键词索引
→ 用户提问
→ 检索相关片段
→ 拼接上下文
→ 调用大模型回答
→ 返回回答和资料来源
```

### 可选向量检索

如果后续升级为真正的向量检索，可以配置：

```powershell
$env:RAG_RETRIEVER_TYPE="vector"
$env:EMBEDDING_API_KEY="你的 Embedding API Key"
$env:EMBEDDING_BASE_URL="你的 Embedding 服务地址"
$env:EMBEDDING_MODEL="你的 Embedding 模型名"
```

注意：

- DeepSeek 聊天模型 Key 不等于 Embedding Key。
- 如果没有单独的 Embedding 服务，请继续使用 `keyword`。
- 向量检索会把资料切片发送给 Embedding 服务生成向量。

向量 RAG 流程：

```text
读取 Markdown 资料
→ 解析元数据
→ 文本切片
→ 调用 Embedding 服务生成向量
→ 写入 Chroma
→ 用户提问
→ 向量检索相关片段
→ 拼接上下文
→ 调用大模型回答
→ 返回回答和资料来源
```

### RAG 验证方式

可以通过接口查看命中的资料片段：

```text
GET /api/rag/search?q=结构体怎么定义
```

如果返回的来源和问题相关，说明检索生效。

如果 RAG 回答里出现来源卡片，并且来源能跳转到知识库详情页，说明前后端链路已经打通。

## 知识库 Markdown 格式

建议每个 Markdown 文件顶部添加元数据：

```markdown
---
title: C 语言指针
topic: C语言
level: 初级
tags: [指针, 地址, 解引用]
---

# C 语言指针

正文内容...
```

元数据用途：

- 知识库卡片展示。
- 资料主题筛选。
- RAG 来源展示。
- 学习计划生成。
- 后续知识推荐。

当前系统内置资料位于：

```text
backend/knowledge
```

已包含示例方向：

- C 语言结构体
- C 语言指针
- Go goroutine
- Go channel
- Java 面向对象
- Java 集合
- Python 基础
- Rust 所有权
- Rust Result
- Vue 3 响应式
- Vue 3 组件通信
- 算法复杂度

## 数据存储说明

### SQLite

默认数据库：

```text
backend/data/programming_assistant.db
```

保存内容：

- 用户账号
- 用户 token
- 用户画像
- 会话历史
- 薄弱点记录
- 学习计划
- 积分信息

### Markdown 资料

系统资料：

```text
backend/knowledge/*.md
```

用户上传资料：

```text
backend/user_knowledge/user_<用户ID>/*.md
```

### RAG 索引

关键词索引：

```text
backend/data/rag_index.json
```

向量索引：

```text
backend/vector_store
```

后端启动时会自动重建知识库索引。

## API 概览

### 基础接口

```text
GET /api/health
GET /api/modes
```

### 登录注册

```text
POST /api/auth/register
POST /api/auth/login
```

### 用户画像与学习档案

```text
GET  /api/profile
PUT  /api/profile
POST /api/profile/reset
GET  /api/profile/insights
```

### 知识库

```text
GET    /api/knowledge
POST   /api/knowledge
GET    /api/knowledge/<file>
DELETE /api/knowledge/<file>
```

### 学习计划

```text
GET    /api/study-plans
POST   /api/study-plans/generate
PUT    /api/study-plans/<id>/steps/<step_index>
POST   /api/study-plans/<id>/summary
DELETE /api/study-plans/<id>
```

### 普通答疑

```text
POST /api/assistant/reply
POST /api/assistant/reply-stream
```

### RAG 答疑

```text
POST /api/rag/rebuild
GET  /api/rag/search
POST /api/rag/reply
POST /api/rag/reply-stream
```

### 会话历史

```text
GET    /api/history
POST   /api/history
DELETE /api/history
DELETE /api/history/<id>
```

### 薄弱点

```text
GET    /api/mistakes
POST   /api/mistakes
PUT    /api/mistakes/<id>
DELETE /api/mistakes/<id>
POST   /api/mistakes/from-assistant
PUT    /api/mistakes/<id>/review
POST   /api/mistakes/<id>/review-question
POST   /api/mistakes/<id>/review-comment
POST   /api/mistakes/<id>/move
POST   /api/mistakes/reorder
```

## 常见问题

### 前端请求失败

先确认后端是否启动：

```text
http://localhost:3000/api/health
```

如果后端未启动，前端页面会无法访问 `/api`。

### DeepSeek 提示缺少 Key

如果看到：

```text
缺少 LLM_API_KEY 或 DEEPSEEK_API_KEY 环境变量
```

说明启动后端的终端没有读取到 Key。

检查：

```powershell
echo $env:DEEPSEEK_API_KEY
echo $env:LLM_API_KEY
echo $env:LLM_BASE_URL
echo $env:LLM_MODEL
```

注意：临时环境变量只对当前 PowerShell 窗口有效。设置完 Key 后，必须在同一个窗口启动后端。

### RAG 没有命中来源

可能原因：

- 问题和知识库资料关系不强。
- 本地资料太少。
- `RAG_MIN_SCORE` 设置过高。
- 当前关键词检索对同义表达不敏感。
- 上传或修改资料后后端没有重新建立索引。

可以用这个接口验证：

```text
GET /api/rag/search?q=你的问题
```

### 自动沉淀薄弱点没有出现

检查：

- 答疑页是否开启“自动沉淀薄弱点”。
- 问题是否是明确的编程学习问题。
- 后端控制台是否有 `[mistake-extraction]` 日志。
- 是否和已有薄弱点重复。
- 模型接口是否可用。

### 前端构建提示 Node 版本

如果看到：

```text
Vite requires Node.js version 20.19+ or 22.12+
```

建议升级 Node.js 到 `20.19+` 或 `22.12+`。

## 当前适合展示的完整流程

### 流程一：答疑到薄弱点

```text
登录
→ 进入智能答疑
→ 开启自动沉淀薄弱点
→ 提问一个编程问题
→ 查看流式回答
→ 查看沉淀结果
→ 进入薄弱点记录
→ 打开 AI 复盘
→ 作答并请求点评
→ 标记掌握获得积分
```

### 流程二：知识库到学习计划

```text
登录
→ 进入知识库
→ 浏览资料卡片
→ 勾选几项资料
→ 生成学习计划
→ 回到首页
→ 勾选完成任务
→ 获得任务积分
→ 完成 100% 后生成阶段总结
```

### 流程三：RAG 知识库增强答疑

```text
进入知识库确认资料存在
→ 进入智能答疑
→ 使用 RAG 答疑
→ 提问和资料相关的问题
→ 查看回答
→ 查看命中来源
→ 点击来源进入资料详情
```

### 流程四：个人资料上传

```text
登录
→ 进入知识库
→ 点击上传个人资料
→ 在弹窗中选择 Markdown 文件或粘贴内容
→ 上传成功
→ 在知识库中看到个人资料卡片
→ 使用 RAG 答疑时参与检索
```

## 后续可扩展方向

- 引入独立 Embedding 服务，完善 Chroma 向量检索。
- 增加 rerank，提高 RAG 命中质量。
- 将薄弱点和知识库资料建立推荐关系。
- 做知识图谱，展示知识点前置关系。
- 增加资料导入管理，例如批量上传、资料分组、资料启用禁用。
- 增加更完整的用户权限和密码安全策略。
- 将答疑、检索、薄弱点沉淀、复盘和学习计划升级为 Agent 工作流。
- 增加学习报告导出能力。
- 增加课程化路线，把知识库资料组织成章节。
