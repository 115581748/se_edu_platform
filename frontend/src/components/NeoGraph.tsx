// frontend/src/components/NeoGraph.tsx
import React, { useEffect, useRef } from "react";
import NeoVis from "neovis.js/dist/neovis.js";

interface NeoGraphProps {
  cypherQuery: string;
  serverUrl: string;
  serverUser: string;
  serverPassword: string;
  onNodeClick?: (node: {
    id: string;
    labels: string[];
    properties: Record<string, any>;
  }) => void;
}

const NeoGraph: React.FC<NeoGraphProps> = ({
  cypherQuery,
  serverUrl,
  serverUser,
  serverPassword,
  onNodeClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  // 存储上一次的 Viz 实例
  const vizRef = useRef<any>(null);
  // 存储上一次的 config，避免重复引用导致的内部错误
  const configRef = useRef<any>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // 如果已经有一个 viz 实例，先清理它
    if (vizRef.current) {
      vizRef.current.clearNetwork();
    }

    // 构造新配置，并保存在 configRef
    const newConfig = {
      container_id: containerRef.current.id,
      server_url: serverUrl,
      server_user: serverUser,
      server_password: serverPassword,
      useNeo4jBolt: true,
      initial_cypher: cypherQuery,
      labels: {
        Concept: { caption: "name" },
        Class:   { caption: "name" },
        // …其他 Label 配置
      },
      relationships: {
        // …你的关系配置
      },
      arrows: true,
    };
    configRef.current = newConfig;

    // 创建新的 Viz 实例并 render
    const viz = new NeoVis(configRef.current);
    vizRef.current = viz;
    viz.render();

    // 渲染完成后，按 status 给节点上色、显示/隐藏 label
    viz.registerOnEvent("renderComplete", () => {
      const network = viz.network;
      const nodesDS  = network.body.data.nodes;
      const allNodes = nodesDS.get();

      allNodes.forEach((node: any) => {
        const status = node.status as string;    // taught / untaught
        const name   = node.name  as string;

        nodesDS.update({
          id: node.id,
          color: {
            background: status === "taught" ? "#10B981" : "#EF4444",
            border:     status === "taught" ? "#047857" : "#B91C1C",
          },
          // 只给“未学”节点显示 label
          label: status === "untaught" ? name : "",
        });
      });

      // 如果传了回调，则注册点击事件
      if (onNodeClick) {
        network.on("click", (params: any) => {
          if (params.nodes.length > 0) {
            const nodeId   = params.nodes[0];
            const nodeData = (viz as any).nodeIdMap[nodeId];
            onNodeClick({
              id: nodeData.id,
              labels: nodeData.labels,
              properties: nodeData.properties,
            });
          }
        });
      }
    });

    // 卸载时清理
    return () => {
      if (vizRef.current) {
        vizRef.current.clearNetwork();
        vizRef.current = null;
      }
    };
  }, [cypherQuery, serverUrl, serverUser, serverPassword, onNodeClick]);

  return (
    <div
      id="neo-vis-container"
      ref={containerRef}
      className="w-full h-[600px] bg-white rounded-lg shadow-md"
    />
  );
};

export default NeoGraph;
