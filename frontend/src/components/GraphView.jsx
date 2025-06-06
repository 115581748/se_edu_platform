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