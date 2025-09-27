import React from "react";
import { useNodesState, useEdgesState, addEdge } from "@xyflow/react";
import type { Connection, NodeTypes  } from "@xyflow/react";
import WorkflowComponent from "./workflowComponent";
import PlaceholderNodeDemo from "../placeholderdemo";

const nodeTypes: NodeTypes = {
  placeholderNode: PlaceholderNodeDemo,
};

const initialNodes = [
  {
    id: "1",
    data: { label: "Original Node" },
    position: { x: 0, y: 0 },
    type: "placeholderNode",
  },
];

const initialEdges = [
  {
    id: "1=>2",
    source: "1",
    target: "2",
    type: "default",
    animated: true,
  },
];

const WorkflowContainer: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = (connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds));
  };

  return (
    <WorkflowComponent
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
    />
  );
};

export default WorkflowContainer;
