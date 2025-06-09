// File: frontend/src/components/NeoGraph.tsx
import React, { useEffect, useRef } from "react";
import NeoVis from "neovis.js/dist/neovis.js";

interface NeoGraphProps {
  serverUrl: string;        // Bolt URL，例如 "bolt://localhost:7687"
  serverUser: string;       // Neo4j 用户名x
  serverPassword: string;   // Neo4j 密码
  status?: string;          // 只渲染此状态的节点，默认 'taught'
  limit?: number;           // 最多拉取多少节点，默认 100
  onNodeClick?: (node: {
    id: string;
    labels: string[];
    properties: Record<string, any>;
  }) => void;
}

const NeoGraph: React.FC<NeoGraphProps> = ({
  serverUrl,
  serverUser,
  serverPassword,
  status = "taught",
  limit = 100,
  onNodeClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const vizRef = useRef<NeoVis | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // 销毁旧实例
    if (vizRef.current) {
      try {
        vizRef.current.clearNetwork();
        // @ts-ignore
        vizRef.current._vis.destroy();
      } catch {}
      vizRef.current = null;
    }

    // 构造带 status 过滤的 Cypher
    const cypher = `
      MATCH (n)
      WHERE n.status = '${status}'
      RETURN n
      LIMIT ${limit}
    `.trim();

    const config = {
      container_id: containerRef.current.id,
      server_url: serverUrl,
      server_user: serverUser,
      server_password: serverPassword,
      useNeo4jBolt: true,
      initial_cypher: cypher,
      labels: {
        // 按需配置不同标签样式
        Concept: { caption: "name", color: "#10B981", size: 18 },
        Framework: { caption: "name", color: "#3B82F6", size: 20 },
        Tool: { caption: "name", color: "#EF4444", size: 16 },
      },
      relationships: {
        RELATED_TO: { caption: false, thickness: 2, color: "#9CA3AF" },
        USES:       { caption: false, thickness: 2, color: "#6B7280" },
      },
      arrows: true,
    };

    const viz = new NeoVis(config);
    vizRef.current = viz;
    viz.render();

    // 节点点击回调
    if (onNodeClick) {
      viz.registerOnEvent("clickNode", (e: any) => {
        if (e.nodes?.length > 0) {
          const nodeId = e.nodes[0];
          // @ts-ignore
          const nodeData = viz.nodeIdMap[nodeId];
          onNodeClick({
            id: nodeData.id,
            labels: nodeData.labels,
            properties: nodeData.properties,
          });
        }
      });
    }

    return () => {
      if (vizRef.current) {
        try {
          vizRef.current.clearNetwork();
          // @ts-ignore
          vizRef.current._vis.destroy();
        } catch {}
        vizRef.current = null;
      }
    };
  }, [serverUrl, serverUser, serverPassword, status, limit, onNodeClick]);

  return (
    <div className="w-full h-[600px] bg-white rounded-lg shadow-md border-gray-200 border" ref={containerRef} id="neo-vis-container" />
  );
};

export default NeoGraph;
