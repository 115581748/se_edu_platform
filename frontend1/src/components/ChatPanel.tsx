// 文件：frontend/src/components/ChatPanel.tsx
import React, { useState } from "react";
import axios from "axios";

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
    // 1. 把用户输入加到 chatList
    const newChatList = [
      ...chatList,
      { role: "user" as const, content: input.trim() },
    ];
    setChatList(newChatList);
    setInput("");
    setLoading(true);

    try {
      // 2. 调用后端 /api/ai/generate
      const resp = await axios.post("/api/ai/generate", {
        prompt: input.trim(),
        // 默认使用 "Concept" label、"taught" 状态，可自行修改
      });
      const answer: string = resp.data.result;

      // 3. 把机器人回答加入 chatList
      setChatList([
        ...newChatList,
        { role: "assistant" as const, content: answer },
      ]);
    } catch (err: any) {
      console.error(err);
      setChatList([
        ...newChatList,
        { role: "assistant" as const, content: "⚠️ 后端调用出错，请检查控制台。" },
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
      <div className="flex-1 overflow-auto p-4">
        {chatList.map((item, idx) => (
          <div
            key={idx}
            className={`mb-4 flex ${
              item.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[70%] p-3 rounded-lg ${
                item.role === "user"
                  ? "bg-primary text-white"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {item.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-center text-gray-500">AI 正在思考…</div>
        )}
      </div>
      <div className="px-4 py-3 border-t border-gray-200 flex items-center space-x-2">
        <input
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
          type="text"
          placeholder="输入你的问题，按回车或点击发送"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          disabled={loading}
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
