import { useRef, useState, useEffect } from "react";
import type { NodeTypes } from "@xyflow/react";
import WorkflowComponent from "./workflowComponent";
import PlaceholderNodeDemo from "../nodes/placeholderdemo";
import BaseHandle from "../nodes/base-handler-demo";
import { useWorkflow } from "@/context/WorkflowContext";
import TriggerNode from "../nodes/trigger-node";
import GoogleSheetsNode from "../nodes/google-sheet";
import TelegramTriggerNode from "../nodes/telegram-trigger-node";
import { useWorkflowNodes } from "../../hooks/useWorkflowNodes";
import { useWorkflowHandlers } from "../../hooks/useWorkflowHandlers";

const nodeTypes: NodeTypes = {
  placeholderNode: PlaceholderNodeDemo,
  MultiplyNode: BaseHandle,
  HttpNode: BaseHandle,
  SchedulerNode: TriggerNode,
  GoogleSheetsNode: GoogleSheetsNode,
  TelegramTriggerNode: TelegramTriggerNode,
};

interface WorkflowContainerProps {
  setOpenRightSidebar: (value: boolean) => void;
  setSelectedNode: (node: any) => void;
  onNodeDelete?: React.Dispatch<React.SetStateAction<((nodeId: number) => Promise<void>) | null>>;
}

const WorkflowContainer: React.FC<WorkflowContainerProps> = ({
  setSelectedNode,
  setOpenRightSidebar,
  onNodeDelete,
}) => {
  const { selectedWorkflowId } = useWorkflow();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });
  const [_, setRfInstance] = useState<any>(null);

  // Use custom hooks for workflow logic
  const {
    nodes,
    setNodes,
    onNodesChange,
    edges,
    setEdges,
    onEdgesChange,
    workflowActive,
    setWorkflowActive,
    createNode,
    updateNode,
    deleteNode,
    createConnection,
    deleteConnection,
    fetchWorkflowNodes,
  } = useWorkflowNodes();

  const {
    handleNodeClick,
    handlePaneClick,
    handleDrop,
    handleConnect,
    handleNodesDelete,
    handleEdgesDelete,
    handleNodeDragStop,
    toggleWorkflowActive,
  } = useWorkflowHandlers({
    selectedWorkflowId,
    edges,
    setNodes,
    setEdges,
    setSelectedNode,
    setOpenRightSidebar,
    createNode,
    updateNode,
    deleteNode,
    createConnection,
    deleteConnection,
    workflowActive,
    setWorkflowActive,
    viewport,
  });

  useEffect(() => {
    if (!selectedWorkflowId) return;

    // Reset nodes and edges immediately so ReactFlow shows empty state
    setNodes([]);
    setEdges([]);

    // Fetch workflow data asynchronously
    fetchWorkflowNodes(selectedWorkflowId);
  }, [selectedWorkflowId]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDropWrapper = (event: React.DragEvent) => {
    handleDrop(event, reactFlowWrapper);
  };

  // Expose the single node delete handler to parent
  useEffect(() => {
    if (onNodeDelete) {
      const handleSingleNodeDelete = async (nodeId: number) => {
        const nodeToDelete = nodes.find((n) => n.id === nodeId.toString());
        if (nodeToDelete) {
          await handleNodesDelete([nodeToDelete]);
          setSelectedNode(null);
          setOpenRightSidebar(false);
        }
      };
      // Use functional setter to store the function in state
      onNodeDelete(() => handleSingleNodeDelete);
    }
  }, [onNodeDelete, nodes, handleNodesDelete, setSelectedNode, setOpenRightSidebar]);

  return (
    <div 
      className="w-full h-full" 
      ref={reactFlowWrapper} 
      onDragOver={(e) => e.preventDefault()} 
      onDrop={handleDropWrapper}
    >
      <WorkflowComponent
        selectedWorkflowId={selectedWorkflowId}
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={handleConnect}
        onNodesDelete={handleNodesDelete}
        onEdgesDelete={handleEdgesDelete}
        onInit={setRfInstance}
        onViewportChange={setViewport}
        onNodeDragStop={handleNodeDragStop}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        workflowActive={workflowActive}
        setWorkflowActive={toggleWorkflowActive}
      />
    </div>
  );
};

export default WorkflowContainer;
