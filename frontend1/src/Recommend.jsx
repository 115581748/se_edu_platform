// src/Recommend.jsx
function Recommend({ items }) {
  return (
    <div>
      <h2>概念推荐</h2>
      {items.length === 0 ? (
        <p>暂无推荐</p>
      ) : (
        <ul>
          {items.map((it, idx) => (
            <li key={idx}>
              <b>{it.concept}</b> — {it.reason}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Recommend;
