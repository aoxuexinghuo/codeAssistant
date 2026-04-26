# 基于大模型的编程答疑助手

一个面向编程学习场景的教学型答疑系统。项目支持多模式问答、流式输出、会话历史、学习资料展示和薄弱点知识卡片管理，后端已切换为 `Flask + LangChain`，后续可继续扩展 `RAG` 和 `Agent` 能力。

## 功能概览

- 智能答疑：支持调试模式、学习模式、面试模式。
- 流式输出：模型回答会逐步显示，降低等待感。
- Markdown 渲染：助手回答和历史记录支持标题、列表、代码块、表格等格式。
- 会话历史：支持查询、清空、删除单条历史、复用历史问题。
- 自动沉淀薄弱点：答疑结束后可自动提取用户可能不熟悉的知识点。
- 薄弱点管理：支持新增、编辑、删除、拖拽排序。
- 学习中心：读取本地 Markdown 知识库，以卡片和详情页形式展示资料。
- 登录注册页面：目前是前端页面原型，可后续接入真实用户体系。

## 技术栈

### 前端

- `Vue 3`
- `Vue Router`
- `Vite`
- `fetch`
- `SSE` 流式接收模型输出
- `marked`：Markdown 解析
- `DOMPurify`：Markdown HTML 清洗

### 后端

- `Python`
- `Flask`
- `Flask-SQLAlchemy`
- `SQLite`
- `LangChain`
- `langchain-openai`
- OpenAI-compatible 模型接口

### 当前数据库

当前使用本地 SQLite：

```text
backend/data/programming_assistant.db
```

目前已持久化：

- 会话历史
- 薄弱点知识卡片

## 项目结构

```text
.
├─ backend
│  ├─ app
│  │  ├─ services
│  │  │  ├─ history_service.py      # 会话历史服务
│  │  │  ├─ llm_service.py          # LangChain 模型调用
│  │  │  ├─ mistake_service.py      # 薄弱点卡片服务
│  │  │  ├─ mode_service.py         # 答疑模式与兜底回复
│  │  │  └─ prompt_service.py       # 答疑提示词
│  │  ├─ __init__.py                # Flask 应用工厂
│  │  ├─ config.py                  # 配置项
│  │  ├─ extensions.py              # Flask 扩展
│  │  ├─ models.py                  # SQLAlchemy 模型
│  │  └─ routes.py                  # API 路由
│  ├─ data                          # SQLite 数据文件目录
│  ├─ requirements.txt
│  ├─ package.json
│  └─ server.py
├─ frontend
│  ├─ src
│  │  ├─ components
│  │  │  ├─ assistant               # 答疑相关组件
│  │  │  ├─ auth                    # 登录注册组件
│  │  │  ├─ common                  # 通用组件
│  │  │  └─ layout                  # 页面布局组件
│  │  ├─ data                       # 学习资料数据
│  │  ├─ router                     # 前端路由
│  │  ├─ services                   # API 请求封装
│  │  ├─ views                      # 页面
│  │  ├─ App.vue
│  │  ├─ main.js
│  │  └─ style.css
│  ├─ package.json
│  └─ vite.config.js
├─ package.json                     # 根目录脚本
└─ README.md
```

说明：

- 根目录下旧的 `src`、`dist` 目录不是当前主要开发入口。
- 当前前端入口在 `frontend/src`。
- 当前后端入口在 `backend/server.py`。

## 环境要求

### Node.js

建议使用：

```text
Node.js >= 20.19.0
```

如果 Node 版本较低，Vite 构建时可能会提示版本警告。

### Python

建议使用：

```text
Python >= 3.10
```

项目当前在 Python 3.12 环境下验证过。

## 安装依赖

在项目根目录安装前端依赖：

```bash
npm install
```

安装后端 Python 依赖：

```bash
python -m pip install -r backend/requirements.txt
```

如果只想单独安装前端依赖，也可以执行：

```bash
npm --prefix frontend install
```

## 模型配置

后端通过 `LangChain` 的 `ChatOpenAI` 接入 OpenAI-compatible 模型服务。

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
```

说明：

- `LLM_API_KEY` 和 `DASHSCOPE_API_KEY` 二选一即可。
- `LLM_BASE_URL` 需要填写兼容 OpenAI 协议的接口地址。
- `LLM_MODEL` 需要填写当前账号可用的模型名称。
- 如果没有配置模型 Key，后端模型调用会失败。

## 启动项目

### 1. 启动后端

在项目根目录执行：

```bash
npm run dev:backend
```

后端默认地址：

```text
http://localhost:3000
```

健康检查：

```text
http://localhost:3000/api/health
```

### 2. 启动前端

新开一个终端，在项目根目录执行：

```bash
npm run dev:frontend
```

前端默认地址：

```text
http://localhost:5173
```

### 3. 访问页面

浏览器打开：

```text
http://localhost:5173
```

前端开发环境会通过 Vite 代理访问后端接口。代理配置位于：

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
```

后端语法检查：

```bash
python -m compileall backend/app
```

## 页面说明

### 首页

首页主要提供学习流程入口：

- 智能答疑
- 薄弱点记录
- 学习中心

### 智能答疑

核心问答页面，包含：

- 三种模式切换
- 问题输入
- 流式回答
- 自动沉淀薄弱点开关
- 会话历史弹窗

三种模式：

- 调试模式：信息不足时优先追问，信息足够时给排查路径。
- 学习模式：用简短结构解释概念，并给最小示例。
- 面试模式：给提示、关键词和答题顺序，默认不直接给完整代码。

### 薄弱点

用于管理学习过程中沉淀的知识卡片：

- 自动生成
- 手动新增
- 编辑修改
- 删除
- 拖拽排序

### 学习中心

学习中心读取 `backend/knowledge` 下的 Markdown 文件，并按主题展示资料卡片。

点击资料卡片后，会进入 Markdown 详情页。

这批 Markdown 同时也是 RAG 检索使用的知识库，因此学习中心和知识库增强答疑共用同一套资料。

## 主要 API

### 基础接口

```text
GET /api/health
GET /api/modes
```

### 答疑接口

```text
POST /api/assistant/reply
POST /api/assistant/reply-stream
```

前端当前主要使用流式接口：

```text
POST /api/assistant/reply-stream
```

请求示例：

```json
{
  "mode": "learning",
  "question": "C语言中结构体怎么定义？"
}
```

### 会话历史接口

```text
GET /api/history
POST /api/history
DELETE /api/history
DELETE /api/history/<id>
```

支持：

- 获取历史
- 新增历史
- 清空历史
- 删除单条历史

### 薄弱点接口

```text
GET /api/mistakes
POST /api/mistakes
PUT /api/mistakes/<id>
DELETE /api/mistakes/<id>
POST /api/mistakes/from-assistant
POST /api/mistakes/<id>/move
POST /api/mistakes/reorder
```

支持：

- 获取薄弱点
- 手动新增
- 编辑卡片
- 删除卡片
- 从答疑结果自动沉淀
- 排序调整

## 自动沉淀薄弱点说明

答疑完成后，如果开启“自动沉淀薄弱点”，前端会调用：

```text
POST /api/mistakes/from-assistant
```

后端会让模型从本轮问答中提取知识点，并保存为薄弱点卡片。

如果模型返回格式不稳定，系统会进行兜底处理：

- 判断问题是否明显属于编程学习问题。
- 如果是，则生成一张简短知识卡片。
- 如果只是寒暄或无明确学习内容，则不生成。

## RAG 框架说明

当前项目已经加入第一版 RAG 框架，采用“本地 Markdown 知识库 + 轻量关键词检索”的方式先跑通整体流程。

当前知识库目录：

```text
backend/knowledge
```

当前索引文件：

```text
backend/data/rag_index.json
```

当前 RAG 服务层：

```text
backend/app/services/embedding_service.py
backend/app/services/retriever_service.py
backend/app/services/rag_service.py
```

当前接口：

```text
POST /api/rag/rebuild
POST /api/rag/reply
```

说明：

- `/api/rag/rebuild` 用于读取 Markdown 并重建本地索引。
- `/api/rag/reply` 用于根据问题检索资料片段，再调用模型生成回答。
- 智能答疑页已加入“知识库增强”开关。
- 开启知识库增强后，回答下方会展示参考来源。
- 当前检索层是轻量实现，后续可以替换为 `Chroma` 或 `FAISS`。
- 后端启动时会自动重建一次 RAG 索引，普通用户无需手动操作。
- RAG 检索会过滤低相关片段，默认最低分数为 `0.25`。
- 后端控制台会打印 `[rag] hit` 或 `[rag] no hit`，用于观察命中文档和分数。

当前已内置示例资料：

```text
backend/knowledge/c-struct.md
backend/knowledge/c-pointer.md
backend/knowledge/java-oop.md
backend/knowledge/java-collections.md
backend/knowledge/python-basics.md
backend/knowledge/go-goroutine.md
backend/knowledge/go-channel.md
backend/knowledge/rust-ownership.md
backend/knowledge/rust-result.md
backend/knowledge/vue-reactivity.md
backend/knowledge/vue-components.md
backend/knowledge/algorithm-complexity.md
```

## 当前提示词策略

为了避免模型回答过长，当前答疑提示词默认要求：

- 不写成长篇教程。
- 默认控制在约 120 字以内。
- 列表最多 3 条。
- 代码最多 8 行。
- 用户未明确要求详细解释时，不主动展开完整知识体系。

如果需要更详细回答，可以在问题中明确写：

```text
请详细解释
请给完整代码
请展开讲
```

## 后续扩展建议

### RAG

当前已完成第一版 RAG 框架。后续可以继续把轻量关键词检索升级为向量检索：

```text
用户问题
→ 检索相关资料
→ 拼接上下文
→ 模型回答
→ 返回引用来源
```

建议后续替换或扩展：

```text
embedding_service.py：接入真实 Embedding
retriever_service.py：替换为 Chroma 或 FAISS 检索
rag_service.py：增加引用片段、相似度阈值和流式输出
```

可选向量库：

- `FAISS`
- `Chroma`

### Agent

后续可以把系统升级为编程学习 Agent，让模型根据问题自动选择工具：

- 查询历史会话
- 查询薄弱点
- 检索知识库
- 新增薄弱点
- 生成答疑回答

推荐先完成 RAG，再引入 Agent，整体会更稳。

### 用户体系

登录注册页面目前是前端原型，后续可以补充：

- 用户注册
- 用户登录
- 密码加密
- Token 鉴权
- 按用户隔离历史记录和薄弱点

## 常见问题

### 1. 前端提示接口失败

先确认后端是否启动：

```text
http://localhost:3000/api/health
```

再确认前端是否通过 Vite 代理访问 `/api`。

### 2. 模型接口调用失败

检查环境变量：

```powershell
echo $env:DASHSCOPE_API_KEY
echo $env:LLM_BASE_URL
echo $env:LLM_MODEL
```

同时确认当前 API Key 是否支持所选模型和调用方式。

### 3. 前端构建出现 Node 版本警告

如果看到类似提示：

```text
Vite requires Node.js version 20.19+ or 22.12+
```

建议升级 Node.js 到 `20.19+` 或 `22.12+`。

### 4. 自动沉淀薄弱点没有出现

检查：

- 答疑页“自动沉淀薄弱点”开关是否开启。
- 后端服务是否已重启。
- 问题是否是明确的编程学习问题。
- 后端控制台是否有 `[mistake-extraction]` 日志。

### 5. 修改代码后页面没变化

前端改动通常会热更新；后端改动需要重启：

```bash
npm run dev:backend
```
