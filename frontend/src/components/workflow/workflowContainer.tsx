import { useRef, useState, useEffect } from "react";
import { useNodesState, useEdgesState } from "@xyflow/react";
import type { NodeTypes } from "@xyflow/react";
import WorkflowComponent from "./workflowComponent";
import PlaceholderNodeDemo from "../placeholderdemo";
import BaseHandle from "../base-handler-demo";
import { useApi } from "../../api/useApi";

const nodeTypes: NodeTypes = {
  placeholderNode: PlaceholderNodeDemo,
  MultiplyNode: BaseHandle,
};

interface WorkflowContainerProps {
  setOpenRightSidebar: (value: boolean) => void;
  setSelectedNode: (node: any) => void;
}

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

const WorkflowContainer:  React.FC<WorkflowContainerProps> = ({ setSelectedNode, setOpenRightSidebar }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNodeType>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<WorkflowEdgeType>([]);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });
  const { callApi } = useApi();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [_, setRfInstance] = useState<any>(null);

  const handleNodeClick = async (_: React.MouseEvent, node: WorkflowNodeType) => {
    console.log("Node clicked", node);
    
    try {
      // 1️⃣ Fetch the UI schema for this node
      const uiSchema = await callApi(`/workflow-nodes/ui-schema/${node.id}`, "GET");
      if (!uiSchema) return;
      
      setSelectedNode(uiSchema); 
      setOpenRightSidebar(true); // open the right sidebar
      console.log("Full node data:", uiSchema);

    } catch (err) {
      console.error("Failed to fetch node UI schema:", err);
    }
  };


  const handlePaneClick = () => {
    setOpenRightSidebar(false); // close the right sidebar
    setSelectedNode(null)
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  };

  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault();
    if (!reactFlowWrapper.current) return;

    const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
    const nodeData = event.dataTransfer.getData("application/reactflow");
    if (!nodeData) return;

    const { type: actualType, id: nodeId } = JSON.parse(nodeData);

    const position = {
      x: (event.clientX - reactFlowBounds.left - viewport.x) / viewport.zoom,
      y: (event.clientY - reactFlowBounds.top - viewport.y) / viewport.zoom,
    };

    try {
      const createdNode = await createWorkflowNode({
        workflow_id: 1,
        node_id: nodeId,
        name: "Send Welcome Email",
        position_x: position.x,
        position_y: position.y
      });

      if (createdNode && createdNode.id) {
        const newNode: WorkflowNodeType = {
          id: createdNode.id.toString(),
          type: "MultiplyNode", // always use BaseHandle mapping
          position: { x: createdNode.position_x, y: createdNode.position_y },
          data: {
            label: createdNode.name,
            customConfig: createdNode.custom_config,
            actualType, // store the real node type here
          },
        };

        setNodes((nds) => [...nds, newNode]);
        console.log("Node successfully added:", newNode);
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
      console.log(workflow)

      const mappedNodes = workflow.nodes.map((node: any) => ({
        id: node.id.toString(),
        type: "MultiplyNode", // always use BaseHandleDemo
        position: { x: node.position_x, y: node.position_y },
        data: {
          content: node.name,            // main label
          customConfig: node.custom_config, 
          actualType: node.node_type,    // pass backend type here
        },
      }));

      const mappedEdges = workflow.connections.map((conn: any) => ({
        id: conn.id,
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
  }) => {
    try {
      const createdNode = await callApi(`/workflow-nodes/`, "POST", node);
      return createdNode;
    } catch (err) {
      console.error("Failed to create workflow node:", err);
      return null;
    }
  };

  const createWorkflowConnection = async (connection: {
    workflow_id: number;
    from_step_id: number;
    to_step_id: number;
    condition: string | null;
  }) => {
    try {
      const createdConnection = await callApi(`/workflow-connections/`, "POST", connection);
      return createdConnection;
    } catch (err) {
      console.error("Failed to create workflow connection:", err);
      return null;
    }
  };

  const handleConnect = async (params: any) => {
    // 0️⃣ Check for duplicates first
    const duplicate = edges.find(
      (edge) =>
        edge.source === params.source && edge.target === params.target
    );

    if (duplicate) {
      console.warn("Connection already exists, skipping creation.");
      return;
    }

    try {
      // 1️⃣ Create the connection in the backend first
      const createdConnection = await createWorkflowConnection({
        workflow_id: 1, // fixed for now
        from_step_id: parseInt(params.source),
        to_step_id: parseInt(params.target),
        condition: null,
      });

      // 2️⃣ Validate backend response
      if (!createdConnection || !createdConnection.id) {
        console.error("Backend returned invalid data, edge not added.");
        return;
      }

      // 3️⃣ If successful, update UI
      const newEdge: WorkflowEdgeType = {
        id: createdConnection.id, // React Flow edge ID
        source: params.source,
        target: params.target,
        type: "simplebezier",
        animated: true,
      };

      setEdges((eds) => [...eds, newEdge]);
      console.log("Connection successfully saved:", createdConnection);

    } catch (error) {
      console.error("Failed to create connection:", error);
    }
  };

  const deleteWorkflowNode = async (nodeId: number) => {
    try {
      // Step 1: Delete the node
      await callApi(`/workflow-nodes/${nodeId}`, "DELETE");
      console.log(`Node ${nodeId} deleted successfully`);
    } catch (err) {
      console.error(`Failed to delete node ${nodeId}:`, err);
      throw err; // bubble up error so we don't remove it from UI incorrectly
    }
  };

  const handleNodesDelete = async (deletedNodes: WorkflowNodeType[]) => {
    for (const node of deletedNodes) {
      const relatedEdges = edges.filter(
        (edge) => edge.source === node.id || edge.target === node.id
      );

      // Delete all related connections
      for (const edge of relatedEdges) {
        await deleteWorkflowConnection(Number(edge.id)); 
      }

      // Delete the node itself
      await deleteWorkflowNode(parseInt(node.id));
    }

    // Update UI locally
    setNodes((nds) => nds.filter((n) => !deletedNodes.some((dn) => dn.id === n.id)));
    setEdges((eds) =>
      eds.filter(
        (edge) =>
          !deletedNodes.some((node) => edge.source === node.id || edge.target === node.id)
      )
    );
  };

  const deleteWorkflowConnection = async (connectionId: number) => {
    try {
      await callApi(`/workflow-connections/${connectionId}`, "DELETE");
      console.log(`Connection ${connectionId} deleted successfully`);
    } catch (err) {
      console.error(`Failed to delete connection ${connectionId}:`, err);
    }
  };

  const handleEdgesDelete = async (deletedEdges: WorkflowEdgeType[]) => {
    console.log(deletedEdges)
    for (const edge of deletedEdges) {
      try {
        // Use backend ID if available, fallback to parsing
        await deleteWorkflowConnection(edge.backendId || edge.id);
      } catch (err) {
        console.error(`Failed to delete connection for edge ${edge.id}:`, err);
      }
    }

    // Remove from local state
    setEdges((eds) => eds.filter((e) => !deletedEdges.some((de) => de.id === e.id)));
  };

  // Handle node drag stop
  const handleNodeDragStop = (_: any, node: any) => {
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
      onConnect={handleConnect}
      onNodesDelete={handleNodesDelete}
      onEdgesDelete={handleEdgesDelete}
      onInit={(instance) => setRfInstance(instance)}
      onViewportChange={(v) => setViewport(v)}
      onNodeDragStop={handleNodeDragStop}
      onNodeClick={handleNodeClick}
      onPaneClick={handlePaneClick} 
    />
  </div>
  );
};

export default WorkflowContainer;
