import React, { useEffect, useState } from "react";
import axios from "axios";

interface Topic {
  name: string;
  labels: string[];
  status: string;  // "learned" or other
}

export const LearnPanel: React.FC = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);

  // 拉取所有 topic（默认 status=null 则返回全部）
  const fetchTopics = async () => {
    setLoading(true);
    try {
      const resp = await axios.get<Topic[]>("/learning/topics");
      setTopics(resp.data);
    } catch (err) {
      console.error("拉取学习进度失败", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  // 标记单个 topic 为已学
  const markLearned = async (name: string) => {
    try {
      await axios.post("/learning/mark", { concept: name });
      // 只更新本地状态，或重新拉取
      setTopics(topics.map(t => t.name === name ? { ...t, status: "taught" } : t));
    } catch (err) {
      console.error("标记已学失败", err);
    }
  };

  const learned   = topics.filter(t => t.status !== "untaught");
  const unlearned = topics.filter(t => t.status === "untaught");

  return (
    <div className="p-4 bg-white rounded-lg shadow-md h-full">
      <h3 className="text-lg font-semibold mb-2">学习进度</h3>
      {loading && <div className="text-gray-500">加载中…</div>}
      <div className="grid grid-cols-2 gap-4">
        {/* 未学过 */}
        <div>
          <h4 className="font-medium text-gray-700 mb-1">未学过</h4>
          <ul className="space-y-1">
            {unlearned.map(t => (
              <li key={t.name} className="flex justify-between items-center">
                <span className="text-sm">{t.name}</span>
                <button
                  className="text-primary hover:underline text-xs"
                  onClick={() => markLearned(t.name)}
                >
                  标记为已学
                </button>
              </li>
            ))}
            {unlearned.length === 0 && <li className="text-xs text-gray-400">全部已学完 🎉</li>}
          </ul>
        </div>
        {/* 已学过 */}
        <div>
          <h4 className="font-medium text-gray-700 mb-1">已学过</h4>
          <ul className="space-y-1">
            {learned.map(t => (
              <li key={t.name} className="flex justify-between items-center">
                <span className="text-sm line-through text-gray-500">{t.name}</span>
                <span className="text-xs text-green-600">✔ 已学</span>
              </li>
            ))}
            {learned.length === 0 && <li className="text-xs text-gray-400">还没学过任何内容</li>}
          </ul>
        </div>
      </div>
    </div>
  );
};
