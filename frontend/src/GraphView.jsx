// src/GraphView.jsx
import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';

function GraphView({ data }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const nodes = data.nodes.map((n) => ({
      data: { id: n.id, label: n.id },
    }));
    const edges = data.links.map((l, idx) => ({
      data: { id: `e${idx}`, source: l.source, target: l.target },
    }));

    const cy = cytoscape({
      container: containerRef.current,
      elements: { nodes, edges },
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'text-valign': 'center',
            'background-color': '#1976d2',
            color: '#fff',
            'text-outline-width': 2,
            'text-outline-color': '#1976d2',
          },
        },
        {
          selector: 'edge',
          style: {
            'line-color': '#999',
            width: 1.5,
          },
        },
      ],
      layout: { name: 'cose', animate: false },
    });

    return () => cy.destroy();
  }, [data]);

  return (
    <div
      ref={containerRef}
      style={{ width: '100%', height: 400, border: '1px solid #ccc', marginTop: 10 }}
    />
  );
}

export default GraphView;
