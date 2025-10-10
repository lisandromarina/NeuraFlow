import React, { useEffect, useState } from "react";
import { useApi } from "../../api/useApi";
import { useWorkflow } from "@/context/WorkflowContext";
import LayoutComponent from "./LayoutComponent";

// Node interface
interface ApiNode {
  id: number;
  name: string;
  type: string;
  category: string;
}

interface SidebarNode {
  id: number;
  title: string;
  category: string;
  type: string;
}

// Workflow interface
interface SidebarWorkflow {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  user_id: number;
}

interface WorkflowType {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  user_id: number;
}

const LayoutContainer: React.FC = () => {
  const { callApi } = useApi();
  const { selectedWorkflowId, setSelectedWorkflowId } = useWorkflow();

  const [nodes, setNodes] = useState<SidebarNode[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false);

  // Fetch nodes
  const fetchNodes = async () => {
    try {
      const data: ApiNode[] = await callApi("/nodes", "GET");
      if (!data) throw new Error("No data returned from API");

      const mappedNodes: SidebarNode[] = data.map((node) => ({
        id: node.id,
        title: node.name,
        category: node.category,
        type: node.type,
      }));

      setNodes(mappedNodes);
    } catch (err: any) {
      console.error("Failed to fetch nodes:", err);
      setError(err.message || "Unknown error");
    }
  };

  // Fetch workflows
  const fetchWorkflows = async () => {
    try {
      const data: SidebarWorkflow[] = await callApi("/workflow/", "GET");
      if (!data) throw new Error("No data returned from API");

      const mappedWorkflows: WorkflowType[] = data.map((wf) => ({
        id: wf.id,
        name: wf.name,
        description: wf.description || "",
        is_active: wf.is_active ?? false,
        user_id: wf.user_id ?? 0,
      }));

      setWorkflows(mappedWorkflows);

      // Set default workflow if none is selected yet
      if (mappedWorkflows.length > 0 && selectedWorkflowId === null) {
        setSelectedWorkflowId(mappedWorkflows[0].id); // choose first workflow as default
      }
    } catch (err: any) {
      console.error("Failed to fetch workflows:", err);
      setError(err.message || "Unknown error");
    }
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchNodes(), fetchWorkflows()]).finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <LayoutComponent
      nodes={nodes}
      workflows={workflows}
      selectedNode={selectedNode}
      setSelectedNode={setSelectedNode}
      isRightSidebarOpen={isRightSidebarOpen}
      setIsRightSidebarOpen={setIsRightSidebarOpen}
    />
  );
};

export default LayoutContainer;
