import React from "react";
import ThemeModeToggle from "../ui/ThemeModeToggle";
import { useAuth } from "@/context/AuthContext";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../ui/dropdown-menu"
import { ChevronUp, User2 } from "lucide-react";

interface Node {
  id: number;
  title: string;
  type: string;
  category: string
}

interface AppSidebarProps {
  nodes: Node[];
}

export function AppSidebar({ nodes }: AppSidebarProps) {
  const { logout } = useAuth();

  const onLogout = () => {
    logout(); 
  };

  const onDragStart = (event: React.DragEvent, node: Node) => {
    event.dataTransfer.setData("application/reactflow", JSON.stringify({
      type: node.type,
      category: node.category,
      title: node.title,
      id: node.id
    }));
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <Sidebar collapsible='icon' className="bg-neutral-100 border-neutral-300">
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
                      <span>{node.title}</span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuButton>
                    <User2 /> Username
                    <ChevronUp className="ml-auto" />
                  </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  side="top"
                  className="w-[--radix-popper-anchor-width]"
                >
                  <DropdownMenuItem>
                    <span>Account</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <span>Billing</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={onLogout}>
                    <span>Sign out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
    </Sidebar>
  );
}
