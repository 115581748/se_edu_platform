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