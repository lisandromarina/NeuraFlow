import React from "react";
import { Background, ReactFlow } from "@xyflow/react";
import type { NodeTypes, Node } from "@xyflow/react";
import WorkflowTogglePanel from "../ui/workflow-toggle-panel";
import { useWorkflow } from "@/context/WorkflowContext";
import { X } from "lucide-react";
import { Button } from "../ui/button";

export interface WorkflowNodeType extends Node {
  type: string; // ensure it's defined, not optional
  category: string;
}

interface WorkflowComponentProps {
  selectedWorkflowId: string | number | null;
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
  onNodeClick?: (event: React.MouseEvent, node: WorkflowNodeType) => void; 
  onPaneClick?: (event: React.MouseEvent) => void;
  workflowActive: boolean;
  setWorkflowActive: (active: boolean) => void;
}

const WorkflowComponent: React.FC<WorkflowComponentProps> = ({
  selectedWorkflowId,
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
  const { nodeForPlacement, setNodeForPlacement } = useWorkflow();

  return (
    <div className="w-full h-full relative">
      <ReactFlow
        key={selectedWorkflowId} 
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
        onPaneClick={(event) => onPaneClick?.(event)}
      >
        <Background />
        <WorkflowTogglePanel
          workflowActive={workflowActive}
          onToggle={() => setWorkflowActive(!workflowActive)}
        />
      </ReactFlow>

      {/* Mobile Placement Mode Banner */}
      {nodeForPlacement && (
        <div className="absolute inset-x-0 top-0 z-50 flex flex-col items-center gap-2 p-4 pointer-events-none">
          <div className="bg-primary text-primary-foreground px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 pointer-events-auto animate-in fade-in slide-in-from-top">
            <div className="flex flex-col">
              <span className="font-semibold text-sm">Tap to place: {nodeForPlacement.title}</span>
              <span className="text-xs opacity-90">Tap on the canvas below</span>
            </div>
          </div>
          <Button 
            size="default"
            variant="secondary"
            className="pointer-events-auto shadow-lg"
            onClick={(e) => {
              e.stopPropagation();
              setNodeForPlacement(null);
            }}
          >
            <X className="h-4 w-4 mr-2" />
            Cancel Placement
          </Button>
        </div>
      )}
    </div>
  );
};

export default WorkflowComponent;
