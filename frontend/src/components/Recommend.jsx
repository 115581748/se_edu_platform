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