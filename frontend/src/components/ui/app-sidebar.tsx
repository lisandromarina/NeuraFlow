import React from "react";
import ThemeModeToggle from "./ThemeModeToggle";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

interface Node {
  id: number;
  title: string;
  type: string;
}

interface AppSidebarProps {
  nodes: Node[];
}

export function AppSidebar({ nodes }: AppSidebarProps) {
  const onDragStart = (event: React.DragEvent, node: Node) => {
    event.dataTransfer.setData("application/reactflow", JSON.stringify({
      type: node.type,
      id: node.id
    }));
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <Sidebar className="bg-neutral-100 border-neutral-300">
      <SidebarContent>
        <SidebarGroup>
          <ThemeModeToggle />
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Nodes</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {nodes?.map((node) => (
                <SidebarMenuItem key={node.id}>
                  <SidebarMenuButton asChild>
                    <div
                      draggable
                      onDragStart={(e) => onDragStart(e, node)}
                      className="flex items-center gap-2 p-2 cursor-pointer hover:bg-gray-200 rounded"
                    >
                      <span>{node.type}</span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
