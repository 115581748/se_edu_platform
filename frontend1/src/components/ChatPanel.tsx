// 文件：frontend/src/components/ChatPanel.tsx
import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";

interface ChatItem {
  role: "user" | "assistant";
  content: string;
}

const ChatPanel: React.FC = () => {
  const [input, setInput] = useState("");
  const [chatList, setChatList] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const message = input.trim();
    setChatList((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setLoading(true);

    try {
      const resp = await axios.post("/api/ai/generate", { prompt: message });
      const answer: string = resp.data.result;
      setChatList((prev) => [
        ...prev,
        { role: "assistant", content: answer },
      ]);
    } catch (err) {
      console.error(err);
      setChatList((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ 后端调用出错，请检查控制台。",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-md">
      <div className="px-4 py-2 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-700">AI 问答面板</h2>
      </div>

      {/* 聊天记录 */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {chatList.map((item, idx) => (
          <div
            key={idx}
            className={`flex ${
              item.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`prose max-w-[70%] p-3 rounded-lg ${
                item.role === "user"
                  ? "bg-primary text-white"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {item.role === "assistant" ? (
                // 渲染 Markdown
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeSanitize]}
                >
                  {item.content}
                </ReactMarkdown>
              ) : (
                // 用户自己输入不需要 Markdown 渲染
                <div>{item.content}</div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="text-center text-gray-500">AI 正在思考…</div>
        )}
      </div>

      {/* 输入框 */}
      <div className="px-4 py-3 border-t border-gray-200 flex items-center space-x-2">
        <textarea
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary resize-none"
          placeholder="输入你的问题，按 Ctrl+Enter 发送"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
              e.preventDefault();
              sendMessage();
            }
          }}
          disabled={loading}
          rows={2}
        />
        <button
          className="bg-primary hover:bg-secondary text-white px-4 py-2 rounded-lg disabled:opacity-50"
          onClick={sendMessage}
          disabled={loading}
        >
          发送
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;
