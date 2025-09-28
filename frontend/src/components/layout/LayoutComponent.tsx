import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "../ui/app-sidebar";
import Workflow from "../workflow";

interface Node {
  id: number;
  title: string;
  type: string;
}

interface LayoutComponentProps {
  nodes: Node[];
}

export default function LayoutComponent({ nodes }: LayoutComponentProps) {
  return (
    <SidebarProvider className="bg-background">
      <AppSidebar nodes={nodes} /> {/* Now nodes match AppSidebar */}
      <SidebarTrigger className="p-auto" />
      <main className="w-full vh-full">
        <Workflow />
      </main>
    </SidebarProvider>
  );
}
