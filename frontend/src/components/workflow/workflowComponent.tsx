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
  onNodeClick?: (node: any) => void;
  onPaneClick?: () => void;
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
  onNodeDragStop,
  onNodeClick,
  onPaneClick
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
        onNodesDelete={onNodesDelete}
        onEdgesDelete={onEdgesDelete}
        fitView
        onInit={onInit}
        onViewportChange={onViewportChange}
        onNodeDragStop={onNodeDragStop} 
        onNodeClick={(node) => onNodeClick?.(node)}
        onPaneClick={() => onPaneClick?.()}
      >
        <Background />
      </ReactFlow>
    </div>
  );
};

export default WorkflowComponent;
