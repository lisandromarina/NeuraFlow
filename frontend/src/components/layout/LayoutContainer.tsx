import React, { useEffect, useState } from "react";
import { useApi } from "../../api/useApi";
import { useWorkflow } from "@/context/WorkflowContext";
import LayoutComponent from "./LayoutComponent";
import { toast } from "sonner";

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

  // Create workflow
  const handleCreateWorkflow = async (name: string, description: string) => {
    try {
      const newWorkflow = await callApi("/workflow/", "POST", {
        name,
        description,
        is_active: false,
        user_id: 1, // TODO: Get from auth context
      });
      toast.success("Workflow created successfully!");
      await fetchWorkflows();
      setSelectedWorkflowId(newWorkflow.id);
    } catch (err: any) {
      toast.error("Failed to create workflow");
      console.error("Failed to create workflow:", err);
      throw err;
    }
  };

  // Delete workflow
  const handleDeleteWorkflow = async (id: number) => {
    try {
      await callApi(`/workflow/${id}`, "DELETE");
      toast.success("Workflow deleted successfully!");
      await fetchWorkflows();
      // Select another workflow if the deleted one was selected
      if (selectedWorkflowId === id) {
        const remainingWorkflows = workflows.filter((wf) => wf.id !== id);
        setSelectedWorkflowId(remainingWorkflows.length > 0 ? remainingWorkflows[0].id : null);
      }
    } catch (err: any) {
      toast.error("Failed to delete workflow");
      console.error("Failed to delete workflow:", err);
      throw err;
    }
  };

  // Toggle workflow active state
  const handleToggleWorkflow = async (id: number) => {
    try {
      const workflow = workflows.find((wf) => wf.id === id);
      if (!workflow) return;

      await callApi(`/workflow/${id}`, "PATCH", {
        is_active: !workflow.is_active,
      });
      
      toast.success(`Workflow ${!workflow.is_active ? "activated" : "paused"}!`);
      await fetchWorkflows();
    } catch (err: any) {
      toast.error("Failed to update workflow");
      console.error("Failed to toggle workflow:", err);
      throw err;
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
      onWorkflowCreate={handleCreateWorkflow}
      onWorkflowDelete={handleDeleteWorkflow}
      onWorkflowToggle={handleToggleWorkflow}
    />
  );
};

export default LayoutContainer;
