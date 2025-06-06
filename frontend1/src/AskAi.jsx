// src/AskAI.jsx
import { useState } from 'react';

function AskAI({ onAsk, loading, answer }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onAsk(input.trim());
  };

  return (
    <div>
      <h2>AI 问答</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入你的问题"
          style={{ width: '60%', padding: 8 }}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? '生成中…' : '提交'}
        </button>
      </form>
      <div style={{ whiteSpace: 'pre-wrap', marginTop: 10 }}>
        {answer && <b>回答：</b>}
        {answer}
      </div>
    </div>
  );
}

export default AskAI;
