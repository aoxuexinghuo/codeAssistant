# 基于大模型的编程答疑助手

一个面向编程学习场景的教学型答疑系统。项目以“编程答疑”为核心，结合 RAG 知识库增强、薄弱点沉淀、AI 复盘、学习计划、任务积分和用户画像，帮助学习者从一次提问延伸到持续复盘和个性化学习。

当前项目采用前后端分离架构：前端使用 Vue 3，后端使用 Flask + LangChain。RAG 模块已经升级为 `Chroma + Embedding` 向量检索方案，支持将本地 Markdown 知识库和用户上传资料切分为 chunk，调用 Embedding 模型生成向量，写入 Chroma 向量数据库，并在答疑时检索相关资料片段作为大模型回答上下文。

## 一、核心功能

### 1. 智能答疑

- 支持调试模式、学习模式、面试模式三种回答策略。
- 支持普通大模型流式输出。
- 支持 RAG 知识库增强流式输出。
- 支持 Markdown 回答渲染，包括代码块、标题、列表等。
- 支持会话历史记录。
- 支持删除单条历史会话。
- 支持自动沉淀薄弱点开关。
- 支持显示薄弱点沉淀结果。
- 支持展示 RAG 命中的知识库来源。
- RAG 来源可以点击跳转到对应知识库资料页。

### 2. RAG 知识库增强

- 使用 Markdown 文件作为本地知识库。
- 支持系统知识库资料。
- 支持用户上传个人 Markdown 资料。
- 使用 chunk 切分知识库文档。
- 使用 Embedding 模型将 chunk 和用户问题转换为向量。
- 使用 Chroma 作为向量检索库。
- 支持 Top-K 相似片段检索。
- 支持相似度阈值过滤。
- 支持用户资料隔离：用户只能检索系统资料和自己的个人资料。
- 支持关键词检索作为异常兜底。

### 3. 知识库

- 展示系统内置学习资料。
- 展示当前用户上传的个人资料。
- 支持按主题筛选资料。
- 支持 Markdown 详情阅读。
- 支持在知识库页弹窗上传个人资料。
- 支持删除当前用户上传的个人资料。
- 支持勾选资料生成学习计划。

### 4. 薄弱点记录

- 支持从答疑过程中自动提炼薄弱知识点。
- 支持手动新增薄弱点。
- 支持编辑薄弱点。
- 支持删除薄弱点。
- 支持拖拽排序。
- 支持搜索和筛选。
- 支持复盘状态：待复盘、复盘中、已掌握。
- 支持 AI 生成复盘问题。
- 支持用户作答后由 AI 给出点评。
- 支持保存复盘内容。
- 支持标记掌握并获得复盘积分。

### 5. 学习计划与积分

- 支持从知识库勾选资料生成学习计划。
- 支持结合用户画像、近期薄弱点和资料内容生成计划。
- 支持首页展示学习计划。
- 支持任务完成状态勾选。
- 每个任务有 1 到 5 分的积分。
- 首次完成任务时获得积分。
- 已获得积分的任务不会重复加分。
- 学习计划完成 100% 后可以生成阶段总结。

### 6. 学习档案与用户画像

- 展示学习等级。
- 展示升级进度。
- 展示提问数量、薄弱点数量、进行中任务和当前方向。
- 展示下一步建议。
- 展示薄弱点诊断。
- 展示近期关注方向。
- 支持维护个人偏好。
- 用户画像会影响答疑提示词和学习计划生成。

### 7. 登录注册与数据隔离

- 支持用户注册。
- 支持用户登录。
- 登录后前端保存用户 token。
- 后续请求通过 `X-User-Token` 识别当前用户。
- 会话历史按用户隔离。
- 薄弱点按用户隔离。
- 学习计划按用户隔离。
- 学习档案按用户隔离。
- 个人上传资料按用户隔离。

## 二、技术栈

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
- SiliconFlow Embedding API
- OpenAI-compatible Chat API
- OpenAI-compatible Embedding API

### 数据与检索

- SQLite：保存用户、会话历史、薄弱点、学习计划和用户画像。
- Markdown：保存系统知识库和用户上传资料。
- Chroma：保存知识库 chunk 的向量表示。
- Embedding 模型：将文档片段和用户问题编码为向量。
- 关键词索引：作为向量检索异常时的兜底方案。

## 三、项目结构

```text
.
├─ backend
│  ├─ app
│  │  ├─ services
│  │  │  ├─ auth_service.py              # 登录注册、token 生成与用户查询
│  │  │  ├─ embedding_service.py         # 关键词兜底分词工具
│  │  │  ├─ history_service.py           # 会话历史增删查
│  │  │  ├─ knowledge_chunk_service.py   # Markdown 清洗与 chunk 切分
│  │  │  ├─ knowledge_service.py         # Markdown 资料读取、上传、删除
│  │  │  ├─ llm_service.py               # LangChain 大模型调用
│  │  │  ├─ markdown_service.py          # Markdown 元数据解析
│  │  │  ├─ mistake_service.py           # 薄弱点生成、编辑、复盘与积分
│  │  │  ├─ mode_service.py              # 答疑模式配置
│  │  │  ├─ profile_service.py           # 用户画像与学习档案
│  │  │  ├─ prompt_service.py            # 提示词构建
│  │  │  ├─ rag_service.py               # RAG 回答编排
│  │  │  ├─ retriever_service.py         # 检索入口，优先 Chroma，失败回退关键词
│  │  │  ├─ schema_service.py            # SQLite 轻量迁移
│  │  │  ├─ study_plan_service.py        # 学习计划生成与任务积分
│  │  │  └─ vector_store_service.py      # Chroma 向量库构建与检索
│  │  ├─ __init__.py                     # Flask 应用工厂
│  │  ├─ config.py                       # 环境变量和目录配置
│  │  ├─ extensions.py                   # Flask 扩展实例
│  │  ├─ models.py                       # SQLAlchemy 数据模型
│  │  └─ routes.py                       # API 路由
│  ├─ data                               # SQLite 数据库和关键词索引
│  ├─ knowledge                          # 系统 Markdown 知识库
│  ├─ user_knowledge                     # 用户上传个人资料
│  ├─ vector_store                       # Chroma 向量数据库目录
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
│  │  ├─ router                          # 路由配置
│  │  ├─ services                        # API 请求与页面状态
│  │  ├─ views                           # 页面视图
│  │  ├─ App.vue
│  │  ├─ main.js
│  │  └─ style.css
├─ package.json
└─ README.md
```

## 四、环境要求

建议版本：

```text
Node.js >= 20.19.0
Python >= 3.10
```

说明：

- Vite 7 推荐 Node.js `20.19+` 或 `22.12+`。
- 后端当前使用 Python + Flask。
- RAG 向量检索需要配置 Embedding API。

## 五、安装依赖

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

## 六、环境变量配置

### 1. DeepSeek 聊天模型配置

DeepSeek 负责生成最终回答。PowerShell 临时配置如下：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-v4-flash"
```

后端读取聊天模型 Key 的优先级：

```text
LLM_API_KEY
→ DEEPSEEK_API_KEY
```

因此也可以写成：

```powershell
$env:LLM_API_KEY="你的 DeepSeek API Key"
```

### 2. Embedding 向量模型配置

Embedding 模型负责把知识库 chunk 和用户问题转换成向量。本项目推荐使用 SiliconFlow 的 `Qwen/Qwen3-Embedding-0.6B`。

PowerShell 临时配置：

```powershell
$env:RAG_RETRIEVER_TYPE="vector"
$env:EMBEDDING_API_KEY="你的 SiliconFlow API Key"
$env:EMBEDDING_BASE_URL="https://api.siliconflow.cn/v1"
$env:EMBEDDING_MODEL="Qwen/Qwen3-Embedding-0.6B"
```

说明：

- `RAG_RETRIEVER_TYPE=vector` 表示使用 Chroma + Embedding 向量检索。
- `EMBEDDING_API_KEY` 是 SiliconFlow 控制台创建的 API Key。
- `EMBEDDING_BASE_URL` 是 OpenAI-compatible Embedding 接口地址。
- `EMBEDDING_MODEL` 是实际使用的向量模型名称。
- DeepSeek 聊天模型 Key 不等于 Embedding Key，两者用途不同。

### 3. 完整启动前配置示例

```powershell
# 聊天模型：负责生成回答
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:LLM_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-v4-flash"

# 向量模型：负责知识库向量化和问题向量化
$env:RAG_RETRIEVER_TYPE="vector"
$env:EMBEDDING_API_KEY="你的 SiliconFlow API Key"
$env:EMBEDDING_BASE_URL="https://api.siliconflow.cn/v1"
$env:EMBEDDING_MODEL="Qwen/Qwen3-Embedding-0.6B"

# RAG 参数
$env:RAG_TOP_K="3"
$env:RAG_MIN_SCORE="0.25"
$env:RAG_CHUNK_SIZE="500"
$env:RAG_CHUNK_OVERLAP="80"
```

然后在同一个 PowerShell 窗口启动后端：

```powershell
npm run dev:backend
```

### 4. 永久环境变量配置

```powershell
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "你的 DeepSeek API Key", "User")
[Environment]::SetEnvironmentVariable("LLM_BASE_URL", "https://api.deepseek.com", "User")
[Environment]::SetEnvironmentVariable("LLM_MODEL", "deepseek-v4-flash", "User")
[Environment]::SetEnvironmentVariable("RAG_RETRIEVER_TYPE", "vector", "User")
[Environment]::SetEnvironmentVariable("EMBEDDING_API_KEY", "你的 SiliconFlow API Key", "User")
[Environment]::SetEnvironmentVariable("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1", "User")
[Environment]::SetEnvironmentVariable("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B", "User")
```

永久配置后需要关闭当前终端，重新打开 PowerShell 后再启动项目。

### 5. 其他可选配置

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

## 七、启动项目

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

## 八、RAG 增强实现说明

本节对应论文中 RAG 增强实现部分，可用于补充“知识库切分 chunk、Embedding 模型、向量检索库 Chroma 的具体配置说明”。

### 1. RAG 总体流程

```text
Markdown 知识库
→ 解析 Markdown 元数据
→ 清洗 Markdown 格式
→ 文本切分为 chunk
→ 调用 Embedding 模型生成向量
→ 写入 Chroma 向量数据库
→ 用户提问
→ 用户问题生成查询向量
→ Chroma 相似度检索 Top-K 片段
→ 过滤低相似度片段
→ 拼接资料片段和用户问题
→ 调用 DeepSeek 生成回答
→ 返回回答和参考来源
```

### 2. 知识库来源

系统知识库目录：

```text
backend/knowledge/*.md
```

用户上传资料目录：

```text
backend/user_knowledge/user_<用户ID>/*.md
```

知识库文件采用 Markdown 格式，建议在文件顶部添加元数据：

```markdown
---
title: Vue 3 组件通信
topic: Vue 3
level: beginner
tags: [props, emit, provide, inject]
---

# Vue 3 组件通信

正文内容...
```

元数据用途：

- 资料卡片展示。
- RAG 来源展示。
- Chroma metadata 存储。
- 用户资料权限过滤。
- 学习计划生成。

### 3. 知识库切分 chunk

代码位置：

```text
backend/app/services/knowledge_chunk_service.py
```

切分前会先对 Markdown 做清洗：

- 移除代码块标记。
- 移除行内代码反引号。
- 移除 Markdown 标题符号。
- 移除部分强调符号。
- 合并多余空白字符。

默认切分参数：

```text
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=80
```

含义：

- `RAG_CHUNK_SIZE=500`：每个知识片段默认约 500 个字符。
- `RAG_CHUNK_OVERLAP=80`：相邻片段之间保留约 80 个字符重叠。

设置 overlap 的原因是避免关键知识点刚好被切断。例如一个概念解释可能横跨两个片段，如果完全无重叠，检索时可能只召回其中一半信息。通过设置 80 字符重叠，可以提高片段语义连续性。

每个 chunk 会保存以下字段：

```text
id          唯一标识，格式类似 system:0:vue-components.md#1
title       资料标题
file        来源文件名
chunkIndex  当前片段编号
content     切分后的文本内容
topic       主题
level       难度
tags        标签
scope       system 或 user
userId      用户 ID，系统资料为 0
```

示例：

```json
{
  "id": "system:0:vue-components.md#1",
  "title": "Vue 3 组件通信",
  "file": "vue-components.md",
  "chunkIndex": 1,
  "topic": "Vue 3",
  "scope": "system",
  "userId": 0
}
```

### 4. Embedding 模型配置

代码位置：

```text
backend/app/services/vector_store_service.py
```

本项目通过 LangChain 的 `OpenAIEmbeddings` 调用 OpenAI-compatible Embedding 接口。推荐配置：

```powershell
$env:EMBEDDING_BASE_URL="https://api.siliconflow.cn/v1"
$env:EMBEDDING_MODEL="Qwen/Qwen3-Embedding-0.6B"
```

选择该模型的原因：

- 适合中文、英文和代码混合文本检索。
- 延迟较低，适合本地毕设演示。
- 成本较低，适合作为轻量级 RAG 项目默认向量模型。
- 使用 OpenAI-compatible 接口，便于与 LangChain 集成。

Embedding 在系统中的两类用途：

```text
文档向量化：Markdown chunk → Embedding 模型 → 文档向量
查询向量化：用户问题 → Embedding 模型 → 查询向量
```

### 5. Chroma 向量检索库配置

代码位置：

```text
backend/app/services/vector_store_service.py
```

向量库存储目录：

```text
backend/vector_store
```

Chroma collection 名称：

```text
programming_assistant_knowledge
```

索引构建逻辑：

```text
读取系统知识库和所有用户上传资料
→ 加载 Markdown 文档
→ 切分 chunk
→ 转换为 LangChain Document
→ 将 chunk metadata 写入 Document metadata
→ 调用 Embedding 模型生成向量
→ 写入 Chroma 持久化目录 backend/vector_store
```

项目启动时会自动重建 RAG 索引。上传或删除个人资料后，也会重建索引，保证新增资料能够参与后续检索。

### 6. 用户资料隔离

Chroma 中同时保存系统资料和用户上传资料，因此必须做权限过滤。

每个 chunk 的 metadata 中包含：

```text
scope: system 或 user
userId: 用户 ID，系统资料为 0
```

检索规则：

```text
未登录用户：只允许检索 scope=system 的系统资料
已登录用户：允许检索 scope=system 的系统资料 + userId=当前用户ID 的个人资料
```

这样可以避免用户 A 上传的个人资料被用户 B 检索到。

### 7. 检索参数

默认检索参数：

```text
RAG_TOP_K=3
RAG_MIN_SCORE=0.25
```

含义：

- `RAG_TOP_K=3`：默认返回相似度最高的 3 个知识片段。
- `RAG_MIN_SCORE=0.25`：低于 0.25 的片段会被过滤。

如果命中结果太少，可以适当降低阈值：

```powershell
$env:RAG_MIN_SCORE="0.2"
```

如果命中结果不够准确，可以适当提高阈值：

```powershell
$env:RAG_MIN_SCORE="0.35"
```

### 8. RAG Prompt 拼接

代码位置：

```text
backend/app/services/rag_service.py
```

检索到资料后，系统会将资料片段拼接成上下文：

```text
[资料 1] Vue 3 组件通信 (vue-components.md)
资料片段正文...

[资料 2] ...
资料片段正文...
```

随后和用户问题一起组成 Prompt：

```text
资料片段：
<检索到的资料内容>

用户问题：<用户问题>

请给出简洁回答。
```

系统提示词要求模型：

- 优先依据给定资料片段回答。
- 如果资料中没有直接依据，需要说明资料库没有找到直接依据。
- 回答控制在 150 字以内。
- 不编造资料来源。
- 结合用户画像中的水平、方向和回答偏好。

### 9. 关键词检索兜底

虽然当前主链路是 Chroma + Embedding，但项目仍保留关键词检索作为兜底。

兜底触发场景：

- Embedding API Key 未配置。
- Embedding 服务不可访问。
- Chroma 索引构建失败。
- 向量检索过程异常。

当向量检索失败时，后端会打印类似日志：

```text
[rag] vector search fallback
```

此时系统会退回关键词检索，避免 RAG 答疑功能完全不可用。

### 10. 成功与失败判断

成功日志示例：

```text
[rag] hit {'question': 'Vue3中，组件之间如何通信?', 'file': 'vue-components.md', 'title': 'Vue 3 组件通信', 'chunkIndex': 1, 'score': 0.4444}
```

说明：

- RAG 检索成功。
- 命中文件为 `vue-components.md`。
- 命中第 1 个 chunk。
- 相似度分数为 `0.4444`。

失败或降级日志示例：

```text
[rag] vector search fallback
```

说明向量检索失败，系统正在回退到关键词检索。

无命中日志示例：

```text
[rag] no hit {'question': 'xxx'}
```

说明 RAG 流程可用，但知识库中没有检索到满足阈值的相关片段。

## 九、论文 5.3.2 可参考描述

本系统的 RAG 增强模块采用“Markdown 知识库 + Embedding 向量化 + Chroma 向量检索库 + 大模型生成”的实现方式。系统首先读取 `backend/knowledge` 目录下的系统知识库文件以及当前用户上传的 Markdown 资料，解析文件顶部的元数据，包括标题、主题、难度和标签等信息。随后系统会对 Markdown 正文进行清洗，去除标题符号、代码块标记和多余空白，并按照固定窗口将文本切分为若干知识片段。默认每个 chunk 大小为 500 个字符，相邻 chunk 保留 80 个字符重叠，以减少知识点被切断导致的语义缺失。

在向量化阶段，系统通过 LangChain 的 `OpenAIEmbeddings` 调用 OpenAI-compatible Embedding 接口。本文选用 SiliconFlow 提供的 `Qwen/Qwen3-Embedding-0.6B` 作为向量模型，将知识库 chunk 和用户问题编码为向量表示。该模型适合中文、英文和代码混合文本检索，并且延迟较低，适合教学型编程答疑系统的本地演示场景。

向量检索库采用 Chroma。系统将每个 chunk 转换为 LangChain Document，并在 metadata 中保存 `title`、`file`、`chunkIndex`、`topic`、`tags`、`scope` 和 `userId` 等字段。Chroma 向量库存储目录为 `backend/vector_store`，collection 名称为 `programming_assistant_knowledge`。系统启动时会自动重建向量索引，用户上传或删除个人资料后也会重建索引，保证知识库内容与向量库保持一致。

用户提问时，系统首先调用同一个 Embedding 模型将问题转换为查询向量，然后在 Chroma 中进行相似度检索。系统默认返回相似度最高的 3 个知识片段，并使用 0.25 作为最低相似度阈值。检索时会根据 metadata 进行权限过滤：未登录用户只能检索系统资料，登录用户可以检索系统资料和自己的个人资料。检索到的片段会被拼接为上下文，与用户问题一起输入大语言模型生成最终回答。通过这种方式，系统可以在回答中结合本地知识库内容，提高回答与课程资料和个人资料的一致性。

## 十、页面说明

### 1. 登录注册页

路由：

```text
/auth/login
/auth/register
```

功能：

- 用户注册。
- 用户登录。
- 登录成功后保存 token 和用户信息。
- 需要登录后才能上传个人资料。

前端本地保存：

```text
programming-assistant-token
programming-assistant-user
```

请求头：

```text
X-User-Token: <token>
```

### 2. 首页

路由：

```text
/home
```

主要模块：

- 今日薄弱点。
- 我的学习计划。
- 学习任务勾选。
- 任务积分反馈。
- 阶段总结入口。
- 智能答疑入口。
- 薄弱点记录入口。
- 知识库入口。

### 3. 智能答疑页

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

主要功能：

- 输入编程问题。
- 切换答疑模式。
- 选择普通答疑或 RAG 答疑。
- 流式输出回答。
- Markdown 格式渲染回答。
- 查看会话历史。
- 删除单条历史。
- 开关自动沉淀薄弱点。
- 显示 RAG 命中来源。

### 4. 知识库页

路由：

```text
/learning
```

说明：页面名称为“知识库”，内部路由仍沿用 `learning`。

功能：

- 展示系统资料。
- 展示当前用户上传的个人资料。
- 按主题筛选资料。
- 查看资料详情。
- 勾选资料生成学习计划。
- 上传个人 Markdown 资料。
- 删除个人上传资料。

上传个人资料入口：

```text
/learning/upload
```

访问该路由时会自动回到知识库页并打开上传弹窗。

### 5. 薄弱点记录页

路由：

```text
/mistakes
```

功能：

- 查看薄弱点卡片。
- 手动新增薄弱点。
- 编辑薄弱点。
- 删除薄弱点。
- 拖拽排序。
- 搜索和筛选。
- AI 复盘。
- AI 点评。
- 标记掌握并获得积分。

### 6. 学习档案页

路由：

```text
/profile
```

主要模块：

- 学习等级。
- 升级进度。
- 状态总览。
- 下一步建议。
- 薄弱点诊断。
- 近期关注方向。
- 个性化策略。
- 个人偏好设置。

## 十一、数据存储说明

### 1. SQLite

默认数据库：

```text
backend/data/programming_assistant.db
```

保存内容：

- 用户账号。
- 用户 token。
- 用户画像。
- 会话历史。
- 薄弱点记录。
- 学习计划。
- 积分信息。

### 2. Markdown 资料

系统资料：

```text
backend/knowledge/*.md
```

用户上传资料：

```text
backend/user_knowledge/user_<用户ID>/*.md
```

### 3. Chroma 向量库

向量库存储目录：

```text
backend/vector_store
```

向量库内容：

- 系统知识库 chunk 向量。
- 用户上传资料 chunk 向量。
- chunk metadata。

### 4. 关键词兜底索引

关键词索引文件：

```text
backend/data/rag_index.json
```

该索引用于向量检索失败后的兜底检索。

## 十二、API 概览

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

## 十三、常用命令

```bash
npm run dev:backend       # 启动 Flask 后端
npm run dev:frontend      # 启动 Vue 前端
npm run build             # 构建前端
npm run build:frontend    # 构建前端
npm run start:backend     # 启动 Flask 后端
python -m compileall backend/app
```

## 十四、常见问题

### 1. 前端请求失败

先确认后端是否启动：

```text
http://localhost:3000/api/health
```

### 2. DeepSeek 提示缺少 Key

如果看到：

```text
缺少 LLM_API_KEY 或 DEEPSEEK_API_KEY 环境变量
```

说明启动后端的终端没有读取到聊天模型 Key。

检查：

```powershell
echo $env:DEEPSEEK_API_KEY
echo $env:LLM_API_KEY
echo $env:LLM_BASE_URL
echo $env:LLM_MODEL
```

### 3. Embedding 配置失败

如果后端控制台出现：

```text
[rag] vector index rebuild skipped
```

或：

```text
[rag] vector search fallback
```

说明 Chroma + Embedding 链路没有正常工作，系统正在回退关键词检索。

需要检查：

```powershell
echo $env:EMBEDDING_API_KEY
echo $env:EMBEDDING_BASE_URL
echo $env:EMBEDDING_MODEL
echo $env:RAG_RETRIEVER_TYPE
```

### 4. RAG 没有命中来源

可能原因：

- 问题和知识库资料关系不强。
- 本地资料太少。
- `RAG_MIN_SCORE` 设置过高。
- Embedding 服务调用失败。
- Chroma 索引没有成功构建。

可以用这个接口验证：

```text
GET /api/rag/search?q=你的问题
```

### 5. 自动沉淀薄弱点没有出现

检查：

- 答疑页是否开启“自动沉淀薄弱点”。
- 问题是否是明确的编程学习问题。
- 后端控制台是否有 `[mistake-extraction]` 日志。
- 是否和已有薄弱点重复。
- 模型接口是否可用。

## 十五、适合展示的完整流程

### 流程一：RAG 知识库增强答疑

```text
启动后端并完成 Chroma 索引构建
→ 进入智能答疑
→ 使用 RAG 答疑
→ 提问和资料相关的问题
→ 查看流式回答
→ 查看参考来源
→ 点击来源进入知识库详情页
```

### 流程二：个人资料参与 RAG

```text
登录
→ 进入知识库
→ 上传个人 Markdown 资料
→ 后端重建 Chroma 索引
→ 进入智能答疑
→ 使用 RAG 提问个人资料相关问题
→ 命中个人资料来源
```

### 流程三：答疑到薄弱点

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

### 流程四：知识库到学习计划

```text
登录
→ 进入知识库
→ 勾选几项资料
→ 生成学习计划
→ 回到首页
→ 勾选完成任务
→ 获得任务积分
→ 完成 100% 后生成阶段总结
```

## 十六、后续可扩展方向

- 引入 rerank 模型，提高 RAG 命中质量。
- 增加知识图谱，展示知识点前置关系。
- 将薄弱点和知识库资料建立推荐关系。
- 增加批量上传、资料分组、资料启用禁用。
- 增加更完整的权限体系和密码安全策略。
- 将答疑、检索、薄弱点沉淀、复盘和学习计划升级为 Agent 工作流。
- 增加学习报告导出能力。
- 增加课程化路线，把知识库资料组织成章节。
