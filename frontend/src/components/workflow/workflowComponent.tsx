import React from "react";
import { Background, ReactFlow } from "@xyflow/react";
import type { NodeTypes } from "@xyflow/react";

interface WorkflowComponentProps {
  nodes: any[];
  edges: any[];
  nodeTypes: NodeTypes;
  onNodesChange: (changes: any) => void;
  onEdgesChange: (changes: any) => void;
  onConnect: (connection: any) => void;
  onInit?: (instance: any) => void;
  onViewportChange?: (viewport: { x: number; y: number; zoom: number }) => void;
  onNodeDragStop?: (event: any, node: any) => void;
}

const WorkflowComponent: React.FC<WorkflowComponentProps> = ({
  nodes,
  edges,
  nodeTypes,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onInit,
  onViewportChange,
  onNodeDragStop
}) => {
  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        onInit={onInit}
        onViewportChange={onViewportChange}
        onNodeDragStop={onNodeDragStop} 
      >
        <Background />
      </ReactFlow>
    </div>
  );
};

export default WorkflowComponent;
