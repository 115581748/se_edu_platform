// frontend/src/App.tsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import ChatPanel from "./components/ChatPanel";
import NeoGraph from "./components/NeoGraph";

export interface Topic {
  name: string;
  labels: string[];
  status: string;
}

const App: React.FC = () => {
  // Neo4j 访问配置
  const NEO4J_URL = "bolt://localhost:7687";
  const NEO4J_USER = "neo4j";
  const NEO4J_PASS = "your_password";

  const GRAPH_CYPHER = `
      // 1) 找到所有 status='taught' 的节点 n
      MATCH (n)-[r]-(m)
      WHERE n.status = 'taught'
      // 2) 返回这对节点和它们之间的关系
      RETURN n, r, m
      LIMIT 200
`;

  // 学习进度状态
  const [untaught, setUntaught] = useState<Topic[]>([]);
  const [taught, setTaught] = useState<Topic[]>([]);
  const [loadingTopics, setLoadingTopics] = useState(false);

  // 拉取指定状态的主题列表
  const fetchTopics = async () => {
    setLoadingTopics(true);
    try {
      const [ru, rt] = await Promise.all([
        axios.get<Topic[]>("/api/learning/topics?status=untaught"),
        axios.get<Topic[]>("/api/learning/topics?status=taught"),
      ]);
      setUntaught(ru.data);
      setTaught(rt.data);
    } catch (e) {
      console.error("加载主题失败", e);
    } finally {
      setLoadingTopics(false);
    }
  };

  // 标记一个主题为已学
  const markLearned = async (name: string) => {
    try {
      await axios.post("/api/learning/mark", { concept: name, user_id: "me" });
      fetchTopics();
    } catch (e) {
      console.error("标记失败", e);
      alert("标记失败，请重试");
    }
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const handleNodeClick = (nodeData: {
    id: string;
    labels: string[];
    properties: Record<string, any>;
  }) => {
    alert(
      `你点击了节点：\nLabel(s) = ${nodeData.labels.join(
        ", "
      )}\nName = ${nodeData.properties.name}`
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-indigo-600">
            AI 驱动的软件工程教育
          </h1>
          <nav className="space-x-4 text-gray-600">
            <a href="#" className="hover:text-indigo-600">首页</a>
            <a href="#" className="hover:text-indigo-600">文档</a>
            <a href="#" className="hover:text-indigo-600">关于我们</a>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧面板：学习进度 + Chat */}
        <section className="space-y-6 lg:col-span-1">
          {/* 学习进度 */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              学习进度
            </h2>
            {loadingTopics ? (
              <div className="text-center text-gray-500">加载中…</div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {/* 未学过 */}
                <div>
                  <h3 className="text-lg font-medium text-red-500 mb-2">未学过</h3>
                  <ul className="space-y-1 max-h-48 overflow-auto">
                    {untaught.map((t) => (
                      <li
                        key={t.name}
                        className="flex items-center justify-between text-sm"
                      >
                        <span>{t.name}</span>
                        <button
                          className="text-xs text-indigo-600 hover:underline"
                          onClick={() => markLearned(t.name)}
                        >
                          标记已学
                        </button>
                      </li>
                    ))}
                    {untaught.length === 0 && (
                      <li className="text-gray-400 text-sm">全都学完啦！</li>
                    )}
                  </ul>
                </div>

                {/* 已学过 */}
                <div>
                  <h3 className="text-lg font-medium text-green-500 mb-2">已学过</h3>
                  <ul className="space-y-1 max-h-48 overflow-auto">
                    {taught.map((t) => (
                      <li key={t.name} className="text-sm text-gray-700">
                        {t.name}
                      </li>
                    ))}
                    {taught.length === 0 && (
                      <li className="text-gray-400 text-sm">还没有已学内容</li>
                    )}
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* ChatPanel */}
          <div className="bg-white p-4 rounded-lg shadow flex-1 h-[500px] flex flex-col">
            <ChatPanel />
          </div>
        </section>

        {/* 右侧：知识图谱 */}
        <section className="lg:col-span-2 bg-white p-4 rounded-lg shadow flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-gray-700">
              知识图谱可视化
            </h2>
            <button
              onClick={() => window.location.reload()}
              className="text-sm text-indigo-600 hover:underline"
            >
              刷新
            </button>
          </div>
          <div className="flex-1">
            <NeoGraph
              cypherQuery={GRAPH_CYPHER}
              serverUrl={NEO4J_URL}
              serverUser={NEO4J_USER}
              serverPassword={NEO4J_PASS}
              onNodeClick={handleNodeClick}
            />
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-8">
        <div className="max-w-7xl mx-auto px-6 py-4 text-center text-gray-500">
          © 2025 AI 学习平台 · All Rights Reserved
        </div>
      </footer>
    </div>
  );
};

export default App;
