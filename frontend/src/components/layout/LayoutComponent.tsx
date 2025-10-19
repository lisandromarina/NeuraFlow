import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "../sidebar/app-sidebar";
import Workflow from "../workflow";
import { RightAppSidebar } from "../sidebar/right-app-sidebar";
import { Toaster } from "@/components/ui/sonner";

interface Node {
  id: number;
  title: string;
  type: string;
  category: string;
}

interface WorkflowType {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  user_id: number;
}

interface LayoutComponentProps {
  nodes: Node[];
  workflows: WorkflowType[];
  selectedNode: any;
  setSelectedNode: (node: any) => void;
  isRightSidebarOpen: boolean;
  setIsRightSidebarOpen: (open: boolean) => void;
  onWorkflowCreate: (name: string, description: string) => Promise<void>;
  onWorkflowDelete: (id: number) => Promise<void>;
  onWorkflowToggle: (id: number) => Promise<void>;
}

export default function LayoutComponent({
  nodes,
  workflows,
  selectedNode,
  setSelectedNode,
  isRightSidebarOpen,
  setIsRightSidebarOpen,
  onWorkflowCreate,
  onWorkflowDelete,
  onWorkflowToggle,
}: LayoutComponentProps) {
  return (
    <div className="h-screen overflow-hidden">
      <Toaster position="top-center"/>
      <SidebarProvider className="bg-background">
        <AppSidebar 
          nodes={nodes} 
          workflows={workflows}
          onWorkflowCreate={onWorkflowCreate}
          onWorkflowDelete={onWorkflowDelete}
          onWorkflowToggle={onWorkflowToggle}
        />
        <main className="w-full">
          <SidebarTrigger className="text-secondary-foreground"/>
          <Workflow
            setOpenRightSidebar={setIsRightSidebarOpen}
            setSelectedNode={setSelectedNode}
          />
        </main>
      </SidebarProvider>

      <SidebarProvider open={isRightSidebarOpen}>
        <RightAppSidebar key={selectedNode?.id} node={selectedNode} />
      </SidebarProvider>
    </div>
  );
}
