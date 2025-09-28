import React from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar";

interface NodeConfig {
  key: string;
  value: any;
}

interface AnotherSidebarProps {
  title?: string;
  config?: NodeConfig[];
}

export function RightAppSidebar({ title = "Node Configuration", config = [] }: AnotherSidebarProps) {
  return (
    <Sidebar side="right" >
      <SidebarTrigger />
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{title}</SidebarGroupLabel>
          <SidebarGroupContent>
            
                <SidebarMenuItem>
                  <div className="p-2 text-gray-500">Select a node to see its configuration</div>
                </SidebarMenuItem>

          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
