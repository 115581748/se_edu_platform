# please_last_project

请毕业是对导师的祈愿，但这个仓库实现的却是一个完整的 AI 驱动教育平台原型。项目以 **Neo4j 知识图谱** 为核心，后端使用 **FastAPI**，前端基于 **React + Vite**，通过整合爬虫脚本和大模型接口，帮助学生管理学习进度并获得代码问题解答。

## 功能概述

- **数据采集脚本**
  - `knowledge_graph_sources.py`：从 Wikipedia、Stack Overflow、GitHub 等渠道抓取技术信息并写入 Neo4j。
  - `GitHub1.py`：爬取指定 GitHub 仓库的 Java 类与方法，构建代码级节点。
  - `stackflow2.py`：获取 Stack Overflow 问答及代码片段，关联到对应类节点。
- **后端接口**（`backend/app.py`）
  - `GET /api/graph-data`：查询图谱数据，可按 `status` 过滤。
  - `POST /api/ai/generate`：结合已学概念调用 DeepSeek-Reasoner 模型生成回答。
  - `POST /api/admin/tag_missing_status`：为没有 `status` 的节点打上默认标记。
  - `GET /api/learning/topics`：按状态列出概念列表。
  - `POST /api/learning/mark`：把指定概念标记为已学。
- **前端界面**
  - `ChatPanel`：向 `/api/ai/generate` 提问并展示回答。
  - `LearnPanel`：显示未学/已学概念列表，支持一键标记。
  - `NeoGraph`：使用 Neovis.js 渲染知识图谱。

## 环境准备

1. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 安装前端依赖：
   ```bash
   cd frontend && npm install
   ```
3. 配置环境变量（可在 `.env` 中设置）：
   - `NEO4J_URI`、`NEO4J_USER`、`NEO4J_PASS`
   - `DEEPSEEK_API_KEY`（调用大模型）
   - 如需采集 GitHub 与 Stack Overflow 数据，可设置 `GITHUB_TOKEN`、`STACK_API_KEY`

## 运行方式

1. 启动或安装 Neo4j，并确保上述连接信息正确。
2. 运行采集脚本写入样例数据，例如：
   ```bash
   python knowledge_graph_sources.py
   ```
3. 启动后端服务：
   ```bash
   uvicorn backend.app:app --reload
   ```
4. 在 `frontend` 目录启动前端：
   ```bash
   npm run dev
   ```
5. 访问浏览器显示的地址，即可查看知识图谱、标记学习状态并向 AI 提问。

## 目录结构

```
backend/        # FastAPI 应用
frontend/       # React + Vite 前端
knowledge_graph_sources.py  # 爬虫脚本示例
GitHub1.py      # GitHub 代码导入
stackflow2.py   # Stack Overflow 数据导入
...
```

## 未来计划

根据 `Advide_from_AI_Total.md` 的规划，后续可以完善推荐算法、引入区块链日志、使用 Docker Compose 部署整套系统等，以持续提升教学体验与可维护性。

