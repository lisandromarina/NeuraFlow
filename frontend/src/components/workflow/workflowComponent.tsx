import React, { useState } from "react";
import { Background, ReactFlow } from "@xyflow/react";
import type { NodeTypes, Node } from "@xyflow/react";
import WorkflowTogglePanel from "../ui/workflow-toggle-panel";

interface WorkflowComponentProps {
  nodes: any[];
  edges: any[];
  nodeTypes: NodeTypes;
  onNodesChange: (changes: any) => void;
  onEdgesChange: (changes: any) => void;
  onConnect: (connection: any) => void;
  onNodesDelete?: (deletedNodes: any[]) => void;
  onEdgesDelete?: (deletedEdges: any[]) => void;
  onInit?: (instance: any) => void;
  onViewportChange?: (viewport: { x: number; y: number; zoom: number }) => void;
  onNodeDragStop?: (event: any, node: any) => void;
  onNodeClick?: (event: React.MouseEvent, node: Node) => void;
  onPaneClick?: () => void;
  workflowActive: boolean;
  setWorkflowActive: (active: boolean) => void;
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
  onPaneClick,
  workflowActive,
  setWorkflowActive
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
        onNodeClick={(event, node) => onNodeClick?.(event, node)}
        onPaneClick={() => onPaneClick?.()}
      >
        <Background />
        <WorkflowTogglePanel
          workflowActive={workflowActive}
          onToggle={() => setWorkflowActive(!workflowActive)}
        />
      </ReactFlow>
    </div>
  );
};

export default WorkflowComponent;
