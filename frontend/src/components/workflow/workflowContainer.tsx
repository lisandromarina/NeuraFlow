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
  const [rfInstance, setRfInstance] = useState<any>(null);

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  };

  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault();
    if (!reactFlowWrapper.current) return;

    const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
    const nodeType = event.dataTransfer.getData("application/reactflow");
    if (!nodeType) return;

    // Convert screen coordinates to canvas coordinates using zoom/pan
    const position = {
      x: (event.clientX - reactFlowBounds.left - viewport.x) / viewport.zoom,
      y: (event.clientY - reactFlowBounds.top - viewport.y) / viewport.zoom,
    };

    try {
      // 1️⃣ Call backend to create node
      const createdNode = await createWorkflowNode({
        workflow_id: 1, // Fixed for now, adjust later
        node_id: 1,     // Adjust if your backend expects different node types
        name: "Send Welcome Email",
        position_x: position.x,
        position_y: position.y,
        custom_config: {
          subject: "Welcome!",
          body: "Thanks for joining our platformasdas.",
        },
      });

      // 2️⃣ Only update state if the API call succeeds
      if (createdNode && createdNode.id) {
        const newNode: WorkflowNodeType = {
          id: createdNode.id.toString(),
          type: nodeType,
          position: {
            x: createdNode.position_x,
            y: createdNode.position_y,
          },
          data: {
            label: createdNode.name,
            customConfig: createdNode.custom_config,
          },
        };

        setNodes((nds) => [...nds, newNode]);

        console.log("Node successfully added:", newNode);
      } else {
        console.error("Failed to create node: API returned invalid data", createdNode);
      }
    } catch (error) {
      console.error("Error creating node:", error);
    }
  };
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

  const createWorkflowNode = async (node: {
    workflow_id: number;
    node_id: number;
    name: string;
    position_x: number;
    position_y: number;
    custom_config: Record<string, any>;
  }) => {
    try {
      const createdNode = await callApi(`/workflow-nodes/`, "POST", node);
      return createdNode;
    } catch (err) {
      console.error("Failed to create workflow node:", err);
      return null;
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
    onDragOver={handleDragOver}
    onDrop={handleDrop}
  >
    <WorkflowComponent
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={(connection) => setEdges((eds) => addEdge(connection, eds))}
      onInit={(instance) => setRfInstance(instance)}
      onViewportChange={(v) => setViewport(v)}
      onNodeDragStop={handleNodeDragStop}
    />
  </div>
  );
};

export default WorkflowContainer;
