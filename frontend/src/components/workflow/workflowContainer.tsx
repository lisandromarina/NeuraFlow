import { useRef, useState, useEffect } from "react";
import { useNodesState, useEdgesState, addEdge } from "@xyflow/react";
import type { NodeTypes } from "@xyflow/react";
import WorkflowComponent from "./workflowComponent";
import PlaceholderNodeDemo from "../placeholderdemo";
import BaseHandle from "../base-handler-demo";
import { useApi } from "../../api/useApi";

const nodeTypes: NodeTypes = {
  placeholderNode: PlaceholderNodeDemo,
  baseHandle: BaseHandle,
};

type WorkflowNodeType = {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: Record<string, any>;
};

type WorkflowEdgeType = {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
  [key: string]: any;
};

const WorkflowContainer: React.FC = () => {
const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNodeType>([]);
const [edges, setEdges, onEdgesChange] = useEdgesState<WorkflowEdgeType>([]);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });
  const { callApi } = useApi();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  // Fetch workflow nodes from backend
  const fetchWorkflowNodes = async (workflowId: number) => {
    try {
      const workflow = await callApi(`/workflow/${workflowId}/full`, "GET");
      if (!workflow) return;

      const mappedNodes = workflow.nodes.map((node: any) => ({
        id: node.id.toString(),
        type: node.node_type,
        position: { x: node.position_x, y: node.position_y },
        data: { label: node.name, ...node.custom_config },
      }));

      const mappedEdges = workflow.connections.map((conn: any) => ({
        id: `${conn.from_step_id}->${conn.to_step_id}`,
        source: conn.from_step_id.toString(),
        target: conn.to_step_id.toString(),
        type: "simplebezier",
        animated: true,
      }));

      setNodes(mappedNodes);
      setEdges(mappedEdges);
    } catch (err) {
      console.error("Failed to fetch workflow nodes:", err);
    }
  };

  // Update workflow node backend safely
  const updateWorkflowNode = async (
    workflowNodeId: number,
    updates: Partial<{ name: string; position_x: number; position_y: number; custom_config: Record<string, any> }>
  ) => {
    try {
      await callApi(`/workflow-nodes/${workflowNodeId}`, "PUT", updates);
    } catch (err) {
      console.error("Failed to update workflow node:", err);
    }
  };

  // Handle node drag stop
  const handleNodeDragStop = (event: any, node: any) => {
    // 1️⃣ Optimistically update local state
    setNodes((nds) =>
      nds.map((n) => (n.id === node.id ? { ...n, position: node.position } : n))
    );
    
    updateWorkflowNode(node.id, {
      position_x: node.position.x,
      position_y: node.position.y,
    });
  };

  useEffect(() => {
    fetchWorkflowNodes(1);
  }, []);

  return (
    <div
      className="w-full h-full"
      ref={reactFlowWrapper}
    >
      <WorkflowComponent
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={(connection) => setEdges((eds) => addEdge(connection, eds))}
        onInit={(instance) => setViewport(instance.viewport)}
        onViewportChange={(v) => setViewport(v)}
        onNodeDragStop={handleNodeDragStop}
      />
    </div>
  );
};

export default WorkflowContainer;
