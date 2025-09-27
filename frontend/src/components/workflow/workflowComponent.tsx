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
  onNodesDelete?: (deletedNodes: any[]) => void;    // NEW
  onEdgesDelete?: (deletedEdges: any[]) => void;    // NEW
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
  onNodesDelete,
  onEdgesDelete,
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
        onNodesDelete={onNodesDelete}    // ✅ Handles node deletion
        onEdgesDelete={onEdgesDelete}    // ✅ Handles edge deletion
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
