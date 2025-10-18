import { useCallback } from 'react';
import { useApi } from '../api/useApi';
import { toast } from 'sonner';
import type { WorkflowNodeType, WorkflowEdgeType } from './useWorkflowNodes';

interface UseWorkflowHandlersProps {
  selectedWorkflowId: number | null;
  edges: WorkflowEdgeType[];
  setNodes: (nodes: WorkflowNodeType[] | ((nodes: WorkflowNodeType[]) => WorkflowNodeType[])) => void;
  setEdges: (edges: WorkflowEdgeType[] | ((edges: WorkflowEdgeType[]) => WorkflowEdgeType[])) => void;
  setSelectedNode: (node: any) => void;
  setOpenRightSidebar: (open: boolean) => void;
  createNode: (node: any) => Promise<any>;
  updateNode: (id: number, updates: any) => Promise<any>;
  deleteNode: (id: number) => Promise<any>;
  createConnection: (conn: any) => Promise<any>;
  deleteConnection: (id: number) => Promise<any>;
  workflowActive: boolean;
  setWorkflowActive: (active: boolean) => void;
  viewport: { x: number; y: number; zoom: number };
}

export const useWorkflowHandlers = ({
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
}: UseWorkflowHandlersProps) => {
  const { callApi } = useApi();

  const safeApi = useCallback(async (fn: () => Promise<any>, fallback: any = null) => {
    try {
      return await fn();
    } catch (err) {
      console.error(err);
      return fallback;
    }
  }, []);

  const handleNodeClick = useCallback(async (_: React.MouseEvent, node: WorkflowNodeType) => {
    const uiSchema = await safeApi(() => callApi(`/workflow-nodes/ui-schema/${node.id}`, "GET"));
    if (!uiSchema) return;
    setSelectedNode(uiSchema);
    setOpenRightSidebar(true);
  }, [safeApi, callApi, setSelectedNode, setOpenRightSidebar]);

  const handlePaneClick = useCallback(() => {
    setOpenRightSidebar(false);
    setSelectedNode(null);
  }, [setOpenRightSidebar, setSelectedNode]);

  const handleDrop = useCallback(async (event: React.DragEvent, reactFlowWrapper: React.RefObject<HTMLDivElement | null>) => {
    event.preventDefault();
    if (!reactFlowWrapper.current || !selectedWorkflowId) return;

    const bounds = reactFlowWrapper.current.getBoundingClientRect();
    const nodeData = event.dataTransfer.getData("application/reactflow");
    if (!nodeData) return;

    const { id, category, title } = JSON.parse(nodeData);
    const position = { 
      x: (event.clientX - bounds.left - viewport.x) / viewport.zoom, 
      y: (event.clientY - bounds.top - viewport.y) / viewport.zoom 
    };

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
  }, [selectedWorkflowId, viewport, createNode, setNodes]);

  const handleConnect = useCallback(async (params: any) => {
    if (edges.some((e) => e.source === params.source && e.target === params.target)) return;

    const created = await createConnection({
      workflow_id: selectedWorkflowId,
      from_step_id: parseInt(params.source),
      to_step_id: parseInt(params.target),
      condition: null,
    });
    if (!created?.id) return;

    setEdges((eds) => [...eds, { ...params, id: created.id, type: "simplebezier", animated: true }]);
  }, [edges, selectedWorkflowId, createConnection, setEdges]);

  const handleNodesDelete = useCallback(async (deletedNodes: WorkflowNodeType[]) => {
    for (const node of deletedNodes) {
      const relatedEdges = edges.filter((e) => e.source === node.id || e.target === node.id);
      await Promise.all(relatedEdges.map((e) => deleteConnection(Number(e.id))));
      await deleteNode(Number(node.id));
    }
    setNodes((nds) => nds.filter((n) => !deletedNodes.some((dn) => dn.id === n.id)));
    setEdges((eds) => eds.filter((e) => !deletedNodes.some((dn) => e.source === dn.id || e.target === dn.id)));
  }, [edges, deleteConnection, deleteNode, setNodes, setEdges]);

  const handleEdgesDelete = useCallback(async (deletedEdges: WorkflowEdgeType[]) => {
    await Promise.all(deletedEdges.map((e) => deleteConnection(e.backendId || e.id)));
    setEdges((eds) => eds.filter((e) => !deletedEdges.some((de) => de.id === e.id)));
  }, [deleteConnection, setEdges]);

  const handleNodeDragStop = useCallback((_: any, node: any) => {
    setNodes((nds) => nds.map((n) => (n.id === node.id ? { ...n, position: node.position } : n)));
    updateNode(node.id, { position_x: node.position.x, position_y: node.position.y });
  }, [setNodes, updateNode]);

  const toggleWorkflowActive = useCallback(async () => {
    const newStatus = !workflowActive;
    setWorkflowActive(newStatus);
    
    await safeApi(() => callApi(`/workflow/${selectedWorkflowId}`, "PUT", { is_active: newStatus }));

    if (newStatus) {
      toast.success("Workflow has been instantiated");
    } else {
      toast.error("Workflow has been Stopped");
    }
  }, [workflowActive, setWorkflowActive, selectedWorkflowId, safeApi, callApi]);

  return {
    handleNodeClick,
    handlePaneClick,
    handleDrop,
    handleConnect,
    handleNodesDelete,
    handleEdgesDelete,
    handleNodeDragStop,
    toggleWorkflowActive,
  };
};
