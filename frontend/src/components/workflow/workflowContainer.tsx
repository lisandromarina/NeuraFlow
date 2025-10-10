import { useRef, useState, useEffect, useCallback } from "react";
import { useNodesState, useEdgesState } from "@xyflow/react";
import type { NodeTypes } from "@xyflow/react";
import WorkflowComponent from "./workflowComponent";
import PlaceholderNodeDemo from "../nodes/placeholderdemo";
import BaseHandle from "../nodes/base-handler-demo";
import { useApi } from "../../api/useApi";
import { useWorkflow } from "@/context/WorkflowContext";
import TriggerNode from "../nodes/trigger-node";

const nodeTypes: NodeTypes = {
  placeholderNode: PlaceholderNodeDemo,
  MultiplyNode: BaseHandle,
  HttpNode: BaseHandle,
  SchedulerService: TriggerNode,
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

const WorkflowContainer: React.FC<WorkflowContainerProps> = ({
  setSelectedNode,
  setOpenRightSidebar,
}) => {
  const { selectedWorkflowId } = useWorkflow();
  const { callApi } = useApi();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  const [workflowActive, setWorkflowActive] = useState(true);
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNodeType>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<WorkflowEdgeType>([]);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });
  const [_, setRfInstance] = useState<any>(null);

  /** Generic safe API wrapper */
  const safeApi = async (fn: () => Promise<any>, fallback: any = null) => {
    try {
      return await fn();
    } catch (err) {
      console.error(err);
      return fallback;
    }
  };

  /** Node/Edge helpers */
  const createNode = (node: any) => safeApi(() => callApi(`/workflow-nodes/`, "POST", node));
  const updateNode = (id: number, updates: any) =>
    safeApi(() => callApi(`/workflow-nodes/${id}`, "PUT", updates));
  const deleteNode = (id: number) => safeApi(() => callApi(`/workflow-nodes/${id}`, "DELETE"));
  const createConnection = (conn: any) =>
    safeApi(() => callApi(`/workflow-connections/`, "POST", conn));
  const deleteConnection = (id: number) =>
    safeApi(() => callApi(`/workflow-connections/${id}`, "DELETE"));

  /** Fetch workflow nodes */
  const fetchWorkflowNodes = useCallback(
    async (workflowId: number) => {
      const workflow = await safeApi(() => callApi(`/workflow/${workflowId}/full`, "GET"));
      if (!workflow) return;

      setWorkflowActive(workflow.is_active);
      setNodes(
        workflow.nodes.map((n: any) => ({
          id: n.id.toString(),
          type: n.node_category,
          position: { x: n.position_x, y: n.position_y },
          data: { content: n.name, customConfig: n.custom_config, actualType: n.node_category },
        }))
      );
      setEdges(
        workflow.connections.map((c: any) => ({
          id: c.id,
          source: c.from_step_id.toString(),
          target: c.to_step_id.toString(),
          type: "simplebezier",
          animated: true,
        }))
      );
    },
    [callApi, setNodes, setEdges]
  );

  /** Node/Edge handlers */
  const handleNodeClick = async (_: React.MouseEvent, node: WorkflowNodeType) => {
    const uiSchema = await safeApi(() => callApi(`/workflow-nodes/ui-schema/${node.id}`, "GET"));
    if (!uiSchema) return;
    setSelectedNode(uiSchema);
    setOpenRightSidebar(true);
  };

  const handlePaneClick = () => {
    setOpenRightSidebar(false);
    setSelectedNode(null);
  };

  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault();
    if (!reactFlowWrapper.current || !selectedWorkflowId) return;

    const bounds = reactFlowWrapper.current.getBoundingClientRect();
    const nodeData = event.dataTransfer.getData("application/reactflow");
    if (!nodeData) return;
    console.log(nodeData)
    const { id, category, title } = JSON.parse(nodeData);
    const position = { x: (event.clientX - bounds.left - viewport.x) / viewport.zoom, y: (event.clientY - bounds.top - viewport.y) / viewport.zoom };

    const created = await createNode({
      workflow_id: selectedWorkflowId,
      node_id: id,
      name: title,
      position_x: position.x,
      position_y: position.y,
    });

    if (created?.id) {
      setNodes((nds) => [
        ...nds,
        {
          id: created.id.toString(),
          type: created.node_category,
          position: { x: created.position_x, y: created.position_y },
          data: { label: created.name, customConfig: created.custom_config, actualType: category },
        },
      ]);
    }
  };

  const handleConnect = async (params: any) => {
    if (edges.some((e) => e.source === params.source && e.target === params.target)) return;

    const created = await createConnection({
      workflow_id: selectedWorkflowId,
      from_step_id: parseInt(params.source),
      to_step_id: parseInt(params.target),
      condition: null,
    });
    if (!created?.id) return;

    setEdges((eds) => [...eds, { ...params, id: created.id, type: "simplebezier", animated: true }]);
  };

  const handleNodesDelete = async (deletedNodes: WorkflowNodeType[]) => {
    for (const node of deletedNodes) {
      const relatedEdges = edges.filter((e) => e.source === node.id || e.target === node.id);
      await Promise.all(relatedEdges.map((e) => deleteConnection(Number(e.id))));
      await deleteNode(Number(node.id));
    }
    setNodes((nds) => nds.filter((n) => !deletedNodes.some((dn) => dn.id === n.id)));
    setEdges((eds) => eds.filter((e) => !deletedNodes.some((dn) => e.source === dn.id || e.target === dn.id)));
  };

  const handleEdgesDelete = async (deletedEdges: WorkflowEdgeType[]) => {
    await Promise.all(deletedEdges.map((e) => deleteConnection(e.backendId || e.id)));
    setEdges((eds) => eds.filter((e) => !deletedEdges.some((de) => de.id === e.id)));
  };

  const handleNodeDragStop = (_: any, node: any) => {
    setNodes((nds) => nds.map((n) => (n.id === node.id ? { ...n, position: node.position } : n)));
    updateNode(node.id, { position_x: node.position.x, position_y: node.position.y });
  };

  const toggleWorkflowActive = async () => {
    const newStatus = !workflowActive;
    setWorkflowActive(newStatus);
    console.log(`/workflow/${selectedWorkflowId}`)
    await safeApi(() => callApi(`/workflow/${selectedWorkflowId}`, "PUT", { is_active: newStatus }));
  };

  /** Effect: fetch workflow whenever selection changes */
  useEffect(() => {
    if (selectedWorkflowId) fetchWorkflowNodes(selectedWorkflowId);
  }, [selectedWorkflowId]);

  return (
    <div className="w-full h-full" ref={reactFlowWrapper} onDragOver={(e) => e.preventDefault()} onDrop={handleDrop}>
      <WorkflowComponent
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
