import { useState, useCallback } from 'react';
import { useNodesState, useEdgesState } from '@xyflow/react';
import { useApi } from '../api/useApi';

export interface WorkflowNodeType {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: Record<string, any>;
}

export interface WorkflowEdgeType {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
  [key: string]: any;
}

export const useWorkflowNodes = () => {
  const { callApi } = useApi();
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNodeType>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<WorkflowEdgeType>([]);
  const [workflowActive, setWorkflowActive] = useState(true);

  // Generic safe API wrapper
  const safeApi = useCallback(async (fn: () => Promise<any>, fallback: any = null) => {
    try {
      return await fn();
    } catch (err) {
      console.error(err);
      return fallback;
    }
  }, []);

  // API helpers
  const createNode = useCallback((node: any) => 
    safeApi(() => callApi(`/workflow-nodes/`, "POST", node)), [safeApi, callApi]);

  const updateNode = useCallback((id: number, updates: any) =>
    safeApi(() => callApi(`/workflow-nodes/${id}`, "PUT", updates)), [safeApi, callApi]);

  const deleteNode = useCallback((id: number) => 
    safeApi(() => callApi(`/workflow-nodes/${id}`, "DELETE")), [safeApi, callApi]);

  const createConnection = useCallback((conn: any) =>
    safeApi(() => callApi(`/workflow-connections/`, "POST", conn)), [safeApi, callApi]);

  const deleteConnection = useCallback((id: number) =>
    safeApi(() => callApi(`/workflow-connections/${id}`, "DELETE")), [safeApi, callApi]);

  // Fetch workflow data
  const fetchWorkflowNodes = useCallback(async (workflowId: number) => {
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
  }, [safeApi, callApi]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
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
  };
};
