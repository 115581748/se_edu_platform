// 文件：frontend/src/App.tsx
import React from "react";
import ChatPanel from "./components/ChatPanel";
import NeoGraph from "./components/NeoGraph";

function App() {
  // Neo4j 访问配置（可改为从 env 变量读入）
  const NEO4J_URL = "bolt://localhost:7687"; // 你的 Neo4j Bolt 访问地址
  const NEO4J_USER = "neo4j"; // 你的 Neo4j 用户名
  const NEO4J_PASS = "your_password";

  // 你想展示的 Cypher 语句，例如把 Class 节点与概念都画出来
  const graphCypher = `
    MATCH (c:Class)-[:RELATED_TO]->(concept:Concept)
    RETURN c, concept
    LIMIT 100
  `;

  // 点击节点时的回调示例
  const handleNodeClick = (nodeData: {
    id: string;
    labels: string[];
    properties: Record<string, any>;
  }) => {
    alert(`你点击了节点：\nLabel(s) = ${nodeData.labels.join(", ")}\nName = ${nodeData.properties.name}`);
  };

  return (
    <div className="min-h-screen flex flex-col bg-muted-50">
      {/* 1. 顶部 Header */}
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-3xl font-heading text-primary">AI 驱动的软件工程教育</h1>
          <nav>
            <a href="#" className="text-gray-600 hover:text-primary px-3">首页</a>
            <a href="#" className="text-gray-600 hover:text-primary px-3">文档</a>
            <a href="#" className="text-gray-600 hover:text-primary px-3">关于我们</a>
          </nav>
        </div>
      </header>

      {/* 2. 主内容区：左右分栏 */}
      <main className="flex-1 container mx-auto px-6 py-8 space-y-6 lg:space-y-0 lg:flex lg:space-x-6">
        {/* 左侧：ChatPanel */}
        <section className="lg:w-1/2 flex flex-col">
          <ChatPanel />
        </section>

        {/* 右侧：NeoGraph */}
        <section className="lg:w-1/2 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-gray-700">知识图谱可视化</h2>
            {/* 你可以放个刷新按钮，调用 NeoGraph 重新绘制 */}
            <button
              onClick={() => window.location.reload()}
              className="text-sm text-secondary hover:text-primary"
            >
              刷新图谱
            </button>
          </div>
          <NeoGraph
            cypherQuery={graphCypher}
            serverUrl={NEO4J_URL}
            serverUser={NEO4J_USER}
            serverPassword={NEO4J_PASS}
            onNodeClick={handleNodeClick}
          />
        </section>
      </main>

      {/* 3. Footer */}
      <footer className="bg-gray-100">
        <div className="container mx-auto px-6 py-4 text-center text-gray-600">
          © 2025 AI 学习平台 · All Rights Reserved
        </div>
      </footer>
    </div>
  );
}

export default App;
