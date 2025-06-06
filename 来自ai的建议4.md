下面给出一个基于 **React** 的前端示例工程，它包括以下核心功能：

1. **问答页面（AskAI）**：输入问题，调用后端 `/ai/generate` 接口，展示 DeepSeek 返回的回答。
2. **知识图谱可视化（GraphView）**：从后端 Neo4j 提供的自定义接口拉取“已标记为 taught”概念及它们的关系，并用 `react-force-graph-2d` 进行可交互式展示。
3. **概念推荐（Recommend）**：调用后端 `/recommend/concepts`（你在后端实现时接口命名可调整）来获取“下一步推荐学习的概念”，并展示在列表中。

你可以基于这个骨架再自行扩展“练习/测验”部分。下面假设你的后端已经启动在 `http://localhost:8000`，并且：

* `POST http://localhost:8000/ai/generate` 返回 `{ result: string }`
* `GET  http://localhost:8000/graph/data` 返回类似于 `{ nodes: [{ id: string }], links: [{ source: string, target: string }] }`
* `POST http://localhost:8000/recommend/concepts` （body: `{ user_id: string, top_k?: number }`）返回类似于 `{ recommendations: [ { concept: string, reason: string } ] }`

下面是一份完整可跑通的 React 工程示例，使用 `Vite + React`（你也可以用 `create-react-app` 或者 Next.js，结构大同小异）。

---

## 工程结构

```
frontend/
├─ public/
│   └─ index.html
├─ src/
│   ├─ components/
│   │   ├─ AskAI.jsx
│   │   ├─ GraphView.jsx
│   │   └─ Recommend.jsx
│   ├─ App.jsx
│   ├─ main.jsx
│   └─ styles.css
├─ package.json
└─ vite.config.js
```

---

## 1. package.json

```jsonc
{
  "name": "edu-kg-frontend",
  "version": "0.0.1",
  "private": true,
  "dependencies": {
    "axios": "^1.4.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-force-graph-2d": "^1.44.1",
    "react-router-dom": "^6.11.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.4.9"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "serve": "vite preview"
  }
}
```

* **axios**：用于与后端 FastAPI 进行 HTTP 通信。
* **react-force-graph-2d**：可视化 Neo4j 知识图谱。
* **react-router-dom**：前端路由，用于在“问答”、“图谱”、“推荐”三页间切换。
* **Vite** + **@vitejs/plugin-react**：搭建 React 开发环境。

---

## 2. vite.config.js

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // 如果后端在 8000，方便开发时跨域转发
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});
```

* 通过 `proxy` 把前端请求 `/api/xxx` 转发到 `http://localhost:8000/xxx`，解决开发时的跨域问题。
* 使用 `vite` 启动后端会一并监听 3000 端口。

---

## 3. public/index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>教育知识图谱 + AI 问答</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  </head>
  <body>
    <div id="root"></div>
    <!-- Vite 会自动注入脚本 -->
  </body>
</html>
```

---

## 4. src/main.jsx

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## 5. src/styles.css

可以按需改，下面只是极简示例：

```css
body {
  margin: 0;
  font-family: sans-serif;
  background-color: #f9fafb;
  color: #1f2937;
}

.navbar {
  background-color: #1f2937;
  color: white;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.navbar a {
  color: white;
  text-decoration: none;
}

.navbar a.active {
  font-weight: bold;
  text-decoration: underline;
}

.container {
  max-width: 960px;
  margin: 20px auto;
  padding: 0 16px;
}

textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 8px;
  resize: vertical;
}

button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
```

---

## 6. src/App.jsx

```jsx
import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';

import AskAI from './components/AskAI';
import GraphView from './components/GraphView';
import Recommend from './components/Recommend';

export default function App() {
  return (
    <BrowserRouter>
      <nav className="navbar">
        <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>
          问答
        </NavLink>
        <NavLink to="/graph" className={({ isActive }) => (isActive ? 'active' : '')}>
          知识图谱
        </NavLink>
        <NavLink to="/recommend" className={({ isActive }) => (isActive ? 'active' : '')}>
          推荐概念
        </NavLink>
      </nav>

      <div className="container">
        <Routes>
          <Route path="/" element={<AskAI />} />
          <Route path="/graph" element={<GraphView />} />
          <Route path="/recommend" element={<Recommend />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
```

* 顶部导航栏包含三项：

  * **问答** → 显示 `AskAI` 组件
  * **知识图谱** → 显示 `GraphView` 组件
  * **推荐概念** → 显示 `Recommend` 组件

---

## 7. src/components/AskAI.jsx

```jsx
import React, { useState } from 'react';
import axios from 'axios';

export default function AskAI() {
  const [prompt, setPrompt] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setLoading(true);
    setAnswer('');
    try {
      // 代理到 http://localhost:8000/ai/generate
      const res = await axios.post('/api/ai/generate', {
        prompt,
        concept_label: 'Concept',
        allowed_status: 'taught',
      });
      setAnswer(res.data.result);
    } catch (err) {
      console.error(err);
      setAnswer('出错了，请稍后再试。');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">AI 问答</h2>
      <form onSubmit={onSubmit} className="mb-4">
        <textarea
          rows={4}
          placeholder="请输入您的问题，比如：“如何在 Spring Boot 中实现单例模式？”"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <div className="mt-2">
          <button type="submit" disabled={loading}>
            {loading ? '生成中…' : '提交问题'}
          </button>
        </div>
      </form>

      <div className="border p-4 rounded min-h-[100px] bg-white">
        <h3 className="font-semibold mb-2">回答：</h3>
        {loading && <p>AI 正在思考…</p>}
        {!loading && <pre className="whitespace-pre-wrap">{answer}</pre>}
      </div>
    </div>
  );
}
```

* 用户输入问题后点击「提交问题」，向后端 `POST /api/ai/generate`，拿到结果后渲染到下方。
* 错误时会在控制台打印并在界面显示“出错了，请稍后再试。”

---

## 8. src/components/GraphView\.jsx

```jsx
import React, { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';

export default function GraphView() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const fgRef = useRef();

  useEffect(() => {
    async function fetchGraph() {
      try {
        // 假设后端暴露：GET /api/graph/data → { nodes: [...], links: [...] }
        const res = await axios.get('/api/graph/data');
        setGraphData(res.data);
      } catch (err) {
        console.error('拉取知识图谱数据失败：', err);
      }
    }
    fetchGraph();
  }, []);

  const handleNodeClick = (node) => {
    // 点击节点时高亮该节点及其一跳邻居
    const neighb = new Set();
    graphData.links.forEach((link) => {
      if (link.source.id === node.id) neighb.add(link.target.id);
      if (link.target.id === node.id) neighb.add(link.source.id);
    });
    fgRef.current.zoomToFit(400, 100, (n) => n.id === node.id || neighb.has(n.id));
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">知识图谱可视化</h2>
      <div className="border rounded" style={{ height: '600px' }}>
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeAutoColorBy="id"
          nodeLabel="id"
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
          onNodeClick={handleNodeClick}
        />
      </div>
      <p className="mt-2 text-sm text-gray-600">
        点击某节点可放大查看该节点及其一跳邻居。
      </p>
    </div>
  );
}
```

* 组件一挂载就向后端 `GET /api/graph/data` 拉取图谱数据，渲染成 `nodes` 与 `links`。
* 点击节点会调用 `zoomToFit` 方法，只放大显示该节点及与其直接相连的邻居。
* 若要攻击节点详情信息（如简介、来源等），可以在点击时再请求后端或在 `graphData.nodes` 里带上更多属性字段，鼠标悬停时直接显示。

---

## 9. src/components/Recommend.jsx

```jsx
import React, { useState } from 'react';
import axios from 'axios';

export default function Recommend() {
  const [userId, setUserId] = useState('student123'); // 示例用一个固定 user_id
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchRecommend = async () => {
    setLoading(true);
    setRecommendations([]);
    try {
      const res = await axios.post('/api/recommend/concepts', {
        user_id: userId,
        top_k: 5
      });
      // 假设后端返回 { recommendations: [ { concept, reason } ] }
      setRecommendations(res.data.recommendations || []);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">智能概念推荐</h2>
      <div className="mb-4">
        <label className="block mb-1">User ID：</label>
        <input
          className="border p-1 rounded w-full"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
      </div>
      <button onClick={fetchRecommend} disabled={loading}>
        {loading ? '加载中…' : '获取推荐'}
      </button>

      <div className="mt-4">
        {recommendations.length === 0 && !loading && <p>暂无推荐，请点击“获取推荐”。</p>}
        {recommendations.map((item, idx) => (
          <div key={idx} className="border p-3 rounded mb-2 bg-white">
            <p>
              <strong>概念：</strong> {item.concept}
            </p>
            <p className="text-sm text-gray-600">
              <strong>理由：</strong> {item.reason}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

* 点击「获取推荐」按钮后，向后端 `POST /api/recommend/concepts` 发送 `{ user_id, top_k }`。
* 后端返回一系列 `{ concept, reason }`，前端展示成卡片式列表。
* 若要进一步点击某个概念跳转到“练习”或“详情”页面，可以再加一个 `onClick` 跳转逻辑。

---

## 10. 后端补充接口示例

为了让上面的前端代码正常运行，请确保你的 FastAPI 后端有以下接口：

```python
from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase

app = FastAPI()
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))

# 1. 问答接口（前文已经实现）：
class GenerateRequest(BaseModel):
    prompt: str
    concept_label: str
    allowed_status: str

class GenerateResponse(BaseModel):
    result: str

@app.post("/ai/generate", response_model=GenerateResponse)
def ai_generate(req: GenerateRequest):
    # ... 按前文逻辑，从 Neo4j 拉取概念，调用 DeepSeek API 等 ...
    return GenerateResponse(result="这里是 AI 回答")


# 2. 知识图谱数据接口
@app.get("/graph/data")
def graph_data():
    with driver.session() as session:
        # 取所有 status="taught" 且标签为 Concept 的节点，以及它们之间的 RELATED_TO 边
        query = """
        MATCH (a:Concept)-[r:RELATED_TO]->(b:Concept)
        WHERE a.status='taught' AND b.status='taught'
        RETURN a.name AS source, b.name AS target
        """
        res = session.run(query)
        const nodesMap = {}
        const links = []
        for rec in res:
            const s = rec["source"]
            const t = rec["target"]
            if s not in nodesMap:
                nodesMap[s] = { "id": s }
            if t not in nodesMap:
                nodesMap[t] = { "id": t }
            links.append({ "source": s, "target": t });
        const nodes = Object.values(nodesMap);
        return { "nodes": nodes, "links": links }
    # 注意：上面是伪代码，真实请用 Python 语法

# 3. 推荐概念接口（示例逻辑）
class RecommendRequest(BaseModel):
    user_id: str
    top_k: int = 5

class RecommendResponse(BaseModel):
    recommendations: list[dict]

@app.post("/recommend/concepts", response_model=RecommendResponse)
def recommend_concepts(req: RecommendRequest):
    # 首先从某处把 student_id 的画像拉出来：假设存在一个表或者存储结构
    # 这里先写一个简化示例：随便推荐几个概念
    demo = [
        { "concept": "Spring Security", "reason": "您对该概念掌握度较低，且它与已学概念关系密切。" },
        { "concept": "Hibernate",       "reason": "推荐复习 Hibernate，以巩固 ORM 基础。" }
    ]
    return RecommendResponse(recommendations=demo[:req.top_k])
```

> **注意**：
>
> * 上面 Python 代码用 `const`、`Object.values` 等是伪示意，请根据前文的 Neo4j 写入 / 读取方式把结果转换成 Python 列表与字典后再 `return`。
> * `graph_data` 接口应返回一个纯粹的 JSON：`{ "nodes": [{ id }], "links": [{ source, target }] }`，以便 `react-force-graph-2d` 直接消费。
> * `recommend/concepts` 可结合你前面在 Neo4j 里对“学生画像”与“概念掌握度”那块的实现，不是简单写死。

---

## 11. 启动与访问

1. 前端目录 `frontend/` 下，先安装依赖：

   ```bash
   cd frontend
   npm install
   ```

2. 启动开发服务器：

   ```bash
   npm run dev
   ```

   * 默认打开 `http://localhost:3000`。
   * 通过 Vite 的 proxy，把对 `/api/...` 的请求转发到 `http://localhost:8000/...`。

3. 后端（FastAPI）需要同时启动（假设在其他终端执行）：

   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

4. 浏览器打开 `http://localhost:3000`，即可看到顶部导航栏：

   * **问答**：在文本框里输入 “如何在 Spring Boot 中实现线程安全的单例模式？”，点击“提交问题”，下方会显示 DeepSeek 的回答。
   * **知识图谱**：会看到已有的 `status="taught"` 的概念节点与它们之间的 `RELATED_TO` 边，可拖拽、缩放、点击高亮。
   * **推荐概念**：点击“获取推荐”按钮，会显示后端返回的“推荐概念 & 理由”列表。

---

## 12. 后续扩展建议

1. **用户登录 & 画像管理**

   * 在前端增加登录页面，用 `FastAPI JWT` 或 OAuth2 实现最简身份验证。
   * 登录后把 `user_id` 存在 `localStorage`，`Recommend` 页面直接用真实 `user_id` 调用 `/recommend/concepts`。
   * 可以在前端做一个“我的学习进度”页面：显示“已掌握概念”、“待掌握概念”，以及用户画像曲线图（grafana / recharts 绘图）。

2. **概念详情与编辑**

   * 在 `GraphView.jsx` 中，除了显示节点 `id`，还可以用 `nodeCanvasObject` 或 `nodeThreeObject` 自定义节点显示：比如 `node.name` 下方标注 `node.status`、`node.tags`。
   * 点击节点后跳转到 `/concept/:name` 路由，显示该概念的详细属性（`description`、`source`、`related_docs`、`stackoverflow_tags` 等），并允许教师在前端修改属性（如更新 `description`、增加关系）。

3. **练习/测验系统**

   * 在前端再增加一页 `Quiz.jsx`，展示题目列表（从后端 `GET /quiz/get/{user_id}` 拉取），用表单形式呈现。
   * 学生提交后调用 `POST /quiz/submit/{quiz_id}`，根据返回结果实时更新“题目正确与否”并更新用户画像。

4. **打分反馈 & 统计报表**

   * 在 `AskAI` 的回答下方放一个“满意度打分”控件（1–5 星），用户打分后前端 `POST /feedback/answer`，后端把评分存到 Neo4j 或单独的表里。
   * 管理员端做一个 `/dashboard` 页面，用图表（recharts、echarts、apexcharts）展示“最近 7 天问答满意度曲线”、“概念通过率”、“最弱概念分析”。

5. **正式部署**

   * 用 Docker Compose 把三部分（Neo4j、FastAPI 后端、React 前端）容器化：

     ```yaml
     version: '3'
     services:
       neo4j:
         image: neo4j:5.13
         environment:
           - NEO4J_AUTH=neo4j/your_password
         ports:
           - "7474:7474"
           - "7687:7687"
         volumes:
           - ./neo4j/data:/data

       backend:
         build:
           context: ./backend
           dockerfile: Dockerfile
         volumes:
           - ./backend:/app
         working_dir: /app
         command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
         ports:
           - "8000:8000"
         depends_on:
           - neo4j

       frontend:
         build:
           context: ./frontend
           dockerfile: Dockerfile
         volumes:
           - ./frontend:/app
         working_dir: /app
         command: npm run dev
         ports:
           - "3000:3000"
         depends_on:
           - backend
     ```
   * 然后 `docker-compose up -d`，即可一键启动整套系统。也可改用 Nginx 做反向代理，把 `/api` 转发给后端，把静态打包后的前端资源直接交给 Nginx。

---

以上这套前端源码示例，可以帮助你快速搭建一个“AI 问答 + 图谱可视化 + 概念推荐”的交互界面。你只需根据自己后端真实接口名称、参数细节做少许改动，就能把整个系统串联起来，并交给老师或学生进行内测。祝你开发顺利！
