# 基于大模型的编程答疑助手

一个面向编程学习场景的教学型答疑系统。项目围绕“提问答疑、知识库增强、薄弱点沉淀、学习计划执行、用户画像”构建，目标是让用户不只是得到答案，还能持续积累自己的学习过程。

## 项目特点

- 支持调试模式、学习模式、面试模式三种答疑策略。
- 支持普通大模型流式回答和 RAG 知识库增强流式回答。
- 支持本地 Markdown 知识库、个人资料上传和资料详情阅读。
- 支持自动沉淀薄弱点，并可手动新增、编辑、删除和拖拽排序。
- 支持生成学习计划，并在首页勾选任务执行状态。
- 支持登录注册，并按用户隔离会话历史、薄弱点、学习计划、学习档案和个人资料。
- 支持用户画像，用于影响回答风格和学习建议。

## 技术栈

### 前端

- Vue 3
- Vue Router
- Vite
- Fetch API
- Server-Sent Events
- marked
- DOMPurify
- 原生 CSS 卡片式界面

### 后端

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- LangChain
- langchain-openai
- Chroma
- DeepSeek API
- OpenAI-compatible 模型接口

## 项目结构

```text
.
├─ backend
│  ├─ app
│  │  ├─ services
│  │  │  ├─ auth_service.py              # 登录注册与 token
│  │  │  ├─ history_service.py           # 会话历史
│  │  │  ├─ knowledge_service.py         # Markdown 资料读取与上传
│  │  │  ├─ knowledge_chunk_service.py   # RAG 文档清洗与切片
│  │  │  ├─ llm_service.py               # LangChain 大模型调用
│  │  │  ├─ markdown_service.py          # Markdown 元数据解析
│  │  │  ├─ mistake_service.py           # 薄弱点卡片
│  │  │  ├─ mode_service.py              # 答疑模式
│  │  │  ├─ profile_service.py           # 用户画像与学习状态
│  │  │  ├─ prompt_service.py            # 答疑提示词
│  │  │  ├─ rag_service.py               # RAG 编排
│  │  │  ├─ retriever_service.py         # 检索入口
│  │  │  ├─ schema_service.py            # SQLite 轻量迁移
│  │  │  ├─ study_plan_service.py        # 学习计划
│  │  │  └─ vector_store_service.py      # Chroma 向量库，可选
│  │  ├─ __init__.py                     # Flask 应用工厂
│  │  ├─ config.py                       # 配置项
│  │  ├─ extensions.py                   # Flask 扩展
│  │  ├─ models.py                       # SQLAlchemy 模型
│  │  └─ routes.py                       # API 路由
│  ├─ data                               # SQLite 与关键词索引
│  ├─ knowledge                          # 系统 Markdown 知识库
│  ├─ user_knowledge                     # 用户上传资料
│  ├─ vector_store                       # Chroma 向量库，可选
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

项目当前在 Python 3.12 环境下验证过。

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

## DeepSeek API 配置

项目后端通过 LangChain 的 `ChatOpenAI` 调用 OpenAI-compatible 接口。当前默认按 DeepSeek 配置：

```text
LLM_BASE_URL 默认值：https://api.deepseek.com
LLM_MODEL 默认值：deepseek-v4-flash
```

PowerShell 临时配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-v4-flash"
$env:RAG_RETRIEVER_TYPE="keyword"
```

临时配置只对当前 PowerShell 窗口有效。请在同一个窗口里继续启动后端：

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

永久配置后需要关闭当前终端，重新打开 PowerShell，再启动后端。

也可以使用通用变量名：

```powershell
$env:LLM_API_KEY="你的 DeepSeek API Key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-v4-flash"
$env:RAG_RETRIEVER_TYPE="keyword"
```

Key 读取优先级：

```text
LLM_API_KEY
→ DEEPSEEK_API_KEY
```

说明：

- `LLM_API_KEY` 和 `DEEPSEEK_API_KEY` 配一个即可。
- 如果同时配置，优先使用 `LLM_API_KEY`。
- `deepseek-v4-flash` 是当前默认模型；如果你的账号更适合其他 DeepSeek 模型，也可以把 `LLM_MODEL` 改成对应模型名。
- DeepSeek 主要用于聊天模型调用；不要把 DeepSeek Key 当成 Embedding Key 使用。

常用可选配置：

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

## RAG 检索配置

当前默认使用关键词检索：

```powershell
$env:RAG_RETRIEVER_TYPE="keyword"
```

这样不需要额外 Embedding 服务，也不会把本地 Markdown 资料发送到第三方向量化接口。

如果后续要启用 Chroma 向量检索，需要额外准备一个 OpenAI-compatible Embedding 服务，并配置：

```powershell
$env:RAG_RETRIEVER_TYPE="vector"
$env:EMBEDDING_API_KEY="你的 Embedding API Key"
$env:EMBEDDING_BASE_URL="你的 Embedding 服务地址"
$env:EMBEDDING_MODEL="你的 Embedding 模型名"
```

注意：DeepSeek Key 不等于 Embedding Key。没有单独 Embedding 服务时，请保持 `RAG_RETRIEVER_TYPE=keyword`。

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

前端通过 Vite 代理访问后端 `/api`，配置文件位于：

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

## 页面功能

### 首页

首页是学习执行入口，主要包含：

- 我的学习计划
- 学习任务完成状态
- 智能答疑入口
- 薄弱点记录入口
- 知识库入口

学习计划可以在首页直接勾选完成状态，也可以删除已有计划。

### 智能答疑

支持三种模式：

```text
调试模式：更偏向追问信息和排查步骤
学习模式：更偏向解释概念和举例
面试模式：更偏向提示和思路引导
```

页面能力：

- 普通流式答疑
- RAG 流式答疑
- Markdown 回答渲染
- 会话历史弹窗
- 单条历史删除
- 自动沉淀薄弱点开关
- 薄弱点沉淀结果提示
- RAG 命中来源展示

### 知识库

知识库展示系统资料和当前用户上传的个人资料。

页面路由仍保留为：

```text
/learning
```

也就是说，用户看到的名称是“知识库”，内部路由暂时仍沿用旧的 `learning` 路径。

资料来源：

```text
backend/knowledge/*.md
backend/user_knowledge/user_<用户ID>/*.md
```

支持：

- 资料卡片浏览
- Markdown 详情页
- 勾选资料生成学习计划
- 上传个人 Markdown 资料
- RAG 来源跳转到对应资料页

上传个人资料入口：

```text
/learning/upload
```

### 薄弱点记录

薄弱点记录用于保存用户在答疑过程中暴露出的知识断点。

支持：

- 答疑后自动沉淀
- 手动新增
- 编辑修改
- 删除单条记录
- 拖拽排序
- 搜索
- 按主题筛选
- 按类型筛选

自动沉淀失败时，后端会使用规则兜底生成更具体的知识点卡片，例如：

```text
结构体定义与成员访问
指针变量、地址与解引用
ref 与 reactive 的使用边界
```

### 学习档案

学习档案当前更偏向“学习诊断页”，用于回答三个问题：

```text
我最近学得怎么样？
我主要卡在哪里？
下一步应该做什么？
```

页面包含：

- 状态总览：累计提问、薄弱点数量、学习计划进度、当前方向。
- 下一步建议：根据学习计划、薄弱点和当前方向给出行动入口。
- 薄弱点诊断：按主题聚合近期薄弱点。
- 画像依据：展示近期关注方向分布和个性化策略。
- 个人偏好：维护回答风格和学习目标。

手动画像包括：

```text
昵称
编程水平
学习方向
学习目标
回答偏好
薄弱点记录偏好
```

自动画像来自：

```text
会话历史
薄弱点记录
答疑模式使用情况
```

画像会影响普通答疑和 RAG 答疑的提示词。

### 登录注册

支持轻量登录注册。

登录成功后前端会保存：

```text
programming-assistant-token
programming-assistant-user
```

后续请求会自动携带：

```text
X-User-Token: <token>
```

当前已按用户隔离：

- 会话历史
- 薄弱点记录
- 学习计划
- 学习档案
- 个人上传资料

## RAG 说明

当前 RAG 支持两种检索方式：

```text
keyword  关键词检索，当前默认方式
vector   Chroma + Embedding 向量检索，需要额外 Embedding 服务
```

关键词检索流程：

```text
读取 Markdown 资料
→ 解析元数据
→ 文本切片
→ 建立关键词索引
→ 用户提问
→ 关键词匹配相关片段
→ 拼接上下文
→ 调用 DeepSeek 回答
→ 返回回答和来源
```

向量检索流程：

```text
读取 Markdown 资料
→ 解析元数据
→ 文本切片
→ 调用 Embedding 服务生成向量
→ 写入 Chroma
→ 用户提问
→ 检索相关片段
→ 拼接上下文
→ 调用 DeepSeek 回答
→ 返回回答和来源
```

后端启动时会自动重建知识库索引。

RAG 相关接口：

```text
POST /api/rag/rebuild
GET  /api/rag/search?q=问题
POST /api/rag/reply
POST /api/rag/reply-stream
```

`/api/rag/search` 可用于查看实际命中的资料片段和分数，方便验证 RAG 是否生效。

## 学习计划说明

学习计划由知识库勾选资料生成。

流程：

```text
知识库勾选资料
→ 生成学习计划
→ 后端结合用户画像、近期薄弱点和所选资料生成任务
→ 保存到当前用户账号
→ 首页展示并执行
```

学习计划包含：

- 计划标题
- 学习目标
- 任务步骤
- 每一步完成状态
- 总体完成进度

生成方式：

- 优先调用大模型生成结构化 JSON。
- 如果模型不可用，使用规则模板兜底生成。

前端不会展示“模型生成 / 规则兜底”等调试标签，保持产品界面简洁。

## 知识库 Markdown 元数据

建议每个 Markdown 文件顶部添加元数据：

```markdown
---
title: C 语言指针
topic: C语言
level: 初级
tags: [指针, 地址, 解引用]
---
```

这些元数据会用于：

- 知识库卡片展示
- RAG 来源展示
- 资料分类
- 学习计划生成

## API 概览

### 基础

```text
GET /api/health
GET /api/modes
```

### 登录注册

```text
POST /api/auth/register
POST /api/auth/login
```

### 学习档案

```text
GET  /api/profile
PUT  /api/profile
POST /api/profile/reset
GET  /api/profile/insights
```

### 学习资料

```text
GET  /api/knowledge
POST /api/knowledge
GET  /api/knowledge/<file>
```

### 学习计划

```text
GET    /api/study-plans
POST   /api/study-plans/generate
PUT    /api/study-plans/<id>/steps/<step_index>
DELETE /api/study-plans/<id>
```

### 普通答疑

```text
POST /api/assistant/reply
POST /api/assistant/reply-stream
```

### RAG

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
POST   /api/mistakes/<id>/move
POST   /api/mistakes/reorder
```

## 常见问题

### 1. 前端接口失败

先确认后端是否启动：

```text
http://localhost:3000/api/health
```

### 2. DeepSeek 接口调用失败

检查环境变量：

```powershell
echo $env:DEEPSEEK_API_KEY
echo $env:LLM_API_KEY
echo $env:LLM_BASE_URL
echo $env:LLM_MODEL
```

推荐最小配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-v4-flash"
$env:RAG_RETRIEVER_TYPE="keyword"
```

如果看到：

```text
LangChain 模型调用失败: baseURL=https://api.deepseek.com model=deepseek-v4-flash reason=缺少 LLM_API_KEY 或 DEEPSEEK_API_KEY 环境变量
```

说明启动后端的那个终端没有读到 Key。需要在同一个 PowerShell 窗口设置环境变量后再执行：

```powershell
npm run dev:backend
```

如果使用 `[Environment]::SetEnvironmentVariable(..., "User")` 做了永久配置，需要关闭并重新打开 PowerShell，旧终端不会自动读取新的用户环境变量。

### 3. RAG 没有命中来源

可能原因：

- 问题和知识库资料相关度不足。
- `RAG_MIN_SCORE` 设置过高。
- Markdown 修改后后端没有重启。
- 当前使用关键词检索，问题表述和资料关键词差异太大。

### 4. 自动沉淀薄弱点没有出现

检查：

- 答疑页“自动沉淀薄弱点”是否开启。
- 问题是否属于明确的编程学习问题。
- 后端控制台是否有 `[mistake-extraction]` 日志。
- 当前问题是否与已有薄弱点重复。

### 5. 前端构建提示 Node 版本

如果看到：

```text
Vite requires Node.js version 20.19+ or 22.12+
```

建议升级 Node.js 到 `20.19+` 或 `22.12+`。

## 后续可扩展方向

- 接入独立 Embedding 服务，升级向量检索。
- 引入 rerank 模型，提高 RAG 命中质量。
- 将薄弱点与知识库资料建立推荐关系。
- 根据学习计划完成情况生成阶段总结。
- 增加知识图谱，展示知识点之间的前置关系。
- 将答疑、检索、薄弱点沉淀和学习计划生成升级为 Agent 工作流。
- 增加更完整的权限体系和密码安全策略。
