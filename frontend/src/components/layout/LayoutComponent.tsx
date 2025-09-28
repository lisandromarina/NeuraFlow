import { useState } from "react";
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
}

export default function LayoutComponent({ nodes }: LayoutComponentProps) {
  const [rightOpen, setRightOpen] = useState(true);

  return (
    <div>
      <SidebarProvider className="bg-background">
        <AppSidebar nodes={nodes} />
        <SidebarTrigger className="p-auto"/>
        <main className="w-full vh-full">
          <Workflow setOpenRightSidebar={setRightOpen}/>
        </main>
      </SidebarProvider>
      <SidebarProvider open={rightOpen} className="bg-background" >
        <RightAppSidebar/>
      </SidebarProvider>
    </div>
  );
}
