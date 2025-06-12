// frontend/src/components/NeoGraph.tsx
import React, { useEffect, useRef } from "react";
import * as NeoVisModule from "neovis.js";

// Compatibility helper to support both ESM and UMD builds
const NeoVis = (NeoVisModule as any).default || (NeoVisModule as any).NeoVis || (NeoVisModule as any);
const { migrateFromOldConfig } = NeoVisModule as any;

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

    // 构造旧版配置并在后续转换为新版格式，避免 2.x 解析错误
    const oldConfig = {
      container_id: containerRef.current.id,
      server_url: serverUrl,
      server_user: serverUser,
      server_password: serverPassword,
      useNeo4jBolt: true,
      initial_cypher: cypherQuery,
      labels: {
        Concept: { caption: "name" },
        Class: { caption: "name" },
        Cloud: { caption: "name" },
        CodeBlock: { caption: "name" },
        Devops: { caption: "name" },
        Framework: { caption: "name" },
        Frontend: { caption: "name" },
        Language: { caption: "name" },
        Library: { caption: "name" },
        Method: { caption: "name" },
        Middleware: { caption: "name" },
        Platfrom: { caption: "name" },
        SOAnswer: { caption: "name" },
        SOQuestion: { caption: "name" },
        Tool: { caption: "name" },
        Tech: { caption: "name" },
        AI: { caption: "name" },
        Database: { caption: "name" },
        // …其他 Label 配置
      },
      relationships: {
        // …你的关系配置
      },
      arrows: true,
    };
    // neovis.js 2.x 使用 camelCase 配置，这里自动转换
    const config = migrateFromOldConfig(oldConfig);
    if (!config.visConfig) {
      config.visConfig = {};
    }
    if (config.visConfig.layout === undefined) {
      config.visConfig.layout = {
        improvedLayout: true,
        hierarchical: { enabled: false, sortMethod: "directed" },
      };
    }
    configRef.current = config;

    // 创建新的 Viz 实例并 render
    const viz = new NeoVis(configRef.current);
    vizRef.current = viz;
    viz.render();

    // 渲染完成后，按 status 给节点上色、显示/隐藏 label
    viz.registerOnEvent("clickNode", () => {
      const network = viz.network;
      const nodesDS  = network.body.data.nodes;
      const allNodes = nodesDS.get();
      console.log(`Total nodes: ${allNodes.length}`);
      console.log("Node details:");
      // 遍历所有节点，设置颜色和 label
      // if (!allNodes || allNodes.length === 0) {
      //   console.warn("No nodes found in the graph.");
      //   return;
      // }
      // // 确保 allNodes 是一个数组
      // if (!Array.isArray(allNodes)) {
      //   console.error("Expected allNodes to be an array, but got:", allNodes);
      //   return;
      // }
      // console.log(`Found ${allNodes.length} nodes in the graph.`);
      // // 遍历所有节点，设置颜色和 label
      // console.log("Setting colors and labels for nodes:");
      // console.log(allNodes);
      // // 遍历所有节点，设置颜色和 label
      // for (const node of allNodes) {
      //   var status = node.raw.properties.status;  // taught / untaught
      //   var name   = node.raw.properties.name;
      //   console.log(`Node ${node.id} status: ${node.raw.properties.status}, name: ${node.raw.properties.name}`);
      //   node.color.background = (status == "taught" ? "#10B981" : "#EF4444");
      //   node.color.border = (status == "taught" ? "#047857" : "#B91C1C");
      //   node.label = (status == "untaught" ? name : "")
      // };

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