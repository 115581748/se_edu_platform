// 文件路径：frontend/src/components/NeoGraph.tsx
import React, { useEffect, useRef } from "react";
import NeoVis, { migrateFromOldConfig } from "neovis.js/dist/neovis.js";

interface NeoGraphProps {
  cypherQuery: string;      // Cypher 查询语句，例如 "MATCH (n) RETURN n LIMIT 100"
  serverUrl: string;        // Neo4j 服务器地址，例如 "bolt://localhost:7687" 或 "neo4j+s://<your-host>"
  serverUser: string;       // Neo4j 用户名，例如 "neo4j"
  serverPassword: string;   // Neo4j 密码，例如 "your_password"
  onNodeClick?: (node: {
    id: string;
    labels: string[];
    properties: Record<string, any>;
  }) => void;
}

/**
 * NeoGraph 组件会：
 * 1. 在顶部显示当前的 serverUser/serverPassword（仅做演示，生产环境请勿明文展示密码）
 * 2. 根据传入的 cypherQuery 调用 Neovis 把结果渲染成一个交互式的知识图谱
 * 3. 当点击某个节点时，如果传了 onNodeClick 回调，就把该节点的 id/labels/properties 传出来
 */
const NeoGraph: React.FC<NeoGraphProps> = ({
  cypherQuery,
  serverUrl,
  serverUser,
  serverPassword,
  onNodeClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const vizRef = useRef<NeoVis | null>(null);

  useEffect(() => {
    console.log("🚀 NeoGraph useEffect 触发，准备渲染图谱");
    const container = containerRef.current;
    if (!container) return;

    // 先销毁之前的实例，避免重复渲染
    if (vizRef.current) {
      try {
        vizRef.current.clearNetwork && vizRef.current.clearNetwork();
        // @ts-ignore
        vizRef.current._vis && vizRef.current._vis.destroy();
      } catch (err) {
        console.warn("销毁旧的 Neovis 实例时出现问题：", err);
      }
      vizRef.current = null;
    }

    // 构造 Neovis 配置
    const oldConfig = {
      container_id: container.id,
      server_url: serverUrl,
      server_user: serverUser,
      server_password: serverPassword,
      initial_cypher: cypherQuery,
      labels: {
        Class: {
          caption: "name",
          size: 20,
          fontColor: "#ffffff",
          community: "type",        // 假设你的节点有 type 属性用于分社区
          highlightFontSize: 14,
          highlightStrokeColor: "#FFD700",
        },
        Concept: {
          caption: "name",
          size: 18,
          fontColor: "#000000",
          community: "category",    // 假设有 category 属性
          highlightStrokeColor: "#10B981",
        },
        // 如果还有其他 Label，请按需配置
        // Framework: { caption: "name", size: 16, fontColor: "#000000", color: "#3B82F6" },
        // Tool: { caption: "name", size: 16, fontColor: "#ffffff", color: "#EF4444" },
      },
      relationships: {
        RELATED_TO: {
          caption: false,
          thickness: 2,
          color: "#9CA3AF",
        },
        USES: {
          caption: false,
          thickness: 2,
          color: "#6B7280",
        },
        // … 其他你在数据中使用的关系类型
      },
      arrows: true,
    };

    // 2.x 开始 neovis.js 改用了 camelCase 配置，为了兼容旧参数，这里自动迁移
    let config = migrateFromOldConfig(oldConfig);
    // 如果布局配置缺失，vis-network 会在 setOptions 时抛出错误，
    // 因此这里为其提供一个默认值
    if (!config.visConfig) {
      config.visConfig = {};
    }
    if (config.visConfig.layout === undefined) {
      config.visConfig.layout = {
        improvedLayout: true,
        hierarchical: { enabled: false, sortMethod: "directed" },
      };
    }

    console.log("📑 Neovis 配置：", config);

    // 实例化并渲染
    const viz = new NeoVis(config);
    vizRef.current = viz;
    viz.render();

    // 如果传了 onNodeClick，就注册点击节点事件
    if (onNodeClick) {
      viz.registerOnEvent("clickNode", (eventData: any) => {
        if (eventData && eventData.nodes && eventData.nodes.length > 0) {
          const clickedNodeId = eventData.nodes[0];
          // Neovis 内部会把节点信息放到 nodeIdMap 中
          // @ts-ignore
          const nodeData = (viz as any).nodeIdMap[clickedNodeId];
          if (nodeData) {
            onNodeClick({
              id: nodeData.id,
              labels: nodeData.labels,
              properties: nodeData.properties,
            });
          }
        }
      });
    }

    // 组件卸载时销毁网络实例
    return () => {
      if (vizRef.current) {
        try {
          vizRef.current.clearNetwork && vizRef.current.clearNetwork();
          // @ts-ignore
          vizRef.current._vis && vizRef.current._vis.destroy();
        } catch (err) {
          console.warn("卸载时销毁 Neovis 实例出错：", err);
        }
        vizRef.current = null;
      }
    };
  }, [cypherQuery, serverUrl, serverUser, serverPassword, onNodeClick]);

  return (
    <div className="space-y-2">
      {/* 在图谱上方显示当前输入的账号/密码（仅作演示，生产环境不要明文展示密码） */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
        <p className="text-sm text-gray-700">
          <span className="font-medium">当前 Neo4j 连接：</span>
          <code className="bg-gray-100 px-1 py-0.5 rounded">{serverUrl}</code>
        </p>
        <p className="text-sm text-gray-700">
          <span className="font-medium">用户名：</span>
          <span className="text-indigo-600">{serverUser}</span>
        </p>
        <p className="text-sm text-red-500">
          <span className="font-medium">密码：</span>
          <span>{serverPassword}</span>
        </p>
      </div>

      {/* 挂载图谱的容器 */}
      <div
        id="neo-vis-container"
        ref={containerRef}
        className="w-full h-[600px] bg-white rounded-lg shadow-md border border-gray-200"
      />
    </div>
  );
};

export default NeoGraph;