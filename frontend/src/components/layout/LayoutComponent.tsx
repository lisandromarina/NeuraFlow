import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "../ui/app-sidebar";
import Workflow from "../workflow";
import { RightAppSidebar } from "../ui/right-app-sidebar";

interface Node {
  id: number;
  title: string;
  type: string;
}

interface LayoutComponentProps {
  nodes: Node[];
  selectedNode: any;
  setSelectedNode: (node: any) => void;
  isRightSidebarOpen: boolean;
  setIsRightSidebarOpen: (open: boolean) => void;
}

export default function LayoutComponent({
  nodes,
  selectedNode,
  setSelectedNode,
  isRightSidebarOpen,
  setIsRightSidebarOpen,
}: LayoutComponentProps) {
  return (
    <div className="h-screen overflow-hidden">
      <SidebarProvider className="bg-background">
        <AppSidebar nodes={nodes} />
        <SidebarTrigger className="p-auto"/>
        <main className="w-full">
          <Workflow 
            setOpenRightSidebar={setIsRightSidebarOpen} 
            setSelectedNode={setSelectedNode}
          />
        </main>
      </SidebarProvider>
      <SidebarProvider open={isRightSidebarOpen}  >
        <RightAppSidebar node={selectedNode}/>
      </SidebarProvider>
    </div>
  );
}
