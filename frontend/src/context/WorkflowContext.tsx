import React, { createContext, useContext, useState } from "react";

interface NodeForPlacement {
  type: string;
  category: string;
  title: string;
  id: number;
}

interface WorkflowContextType {
  selectedWorkflowId: number | null;
  setSelectedWorkflowId: (id: number | null) => void;
  nodeForPlacement: NodeForPlacement | null;
  setNodeForPlacement: (node: NodeForPlacement | null) => void;
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined);

export const WorkflowProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<number | null>(null);
  const [nodeForPlacement, setNodeForPlacement] = useState<NodeForPlacement | null>(null);

  return (
    <WorkflowContext.Provider value={{ 
      selectedWorkflowId, 
      setSelectedWorkflowId,
      nodeForPlacement,
      setNodeForPlacement
    }}>
      {children}
    </WorkflowContext.Provider>
  );
};

export const useWorkflow = () => {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error("useWorkflow must be used within a WorkflowProvider");
  }
  return context;
};
