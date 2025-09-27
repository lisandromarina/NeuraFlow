import { SquarePen, Search } from "lucide-react"
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
} from "@/components/ui/sidebar"

// Menu items.
const items = [
  {
    title: "New Chat",
    url: "#",
    icon: SquarePen,
  },
  {
    title: "Search Chat",
    url: "#",
    icon: Search,
  }
]

const workflowNodes = [
  { title: "Trigger Node", type: "baseHandle" },
  { title: "Action Node", type: "baseHandle" },
  { title: "Condition Node", type: "baseHandle" },
];

const onDragStart = (event: React.DragEvent, nodeType: string) => {
  event.dataTransfer.setData("application/reactflow", nodeType);
  event.dataTransfer.effectAllowed = "move";
};

export function AppSidebar() {
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
              {workflowNodes.map((node) => (
                <SidebarMenuItem key={node.type}>
                  <SidebarMenuButton asChild>
                    <div
                      draggable
                      onDragStart={(e) => onDragStart(e, node.type)}
                      className="flex items-center gap-2 p-2 cursor-pointer hover:bg-gray-200 rounded"
                    >
                      {/* Optional icon */}
                      <span>{node.title}</span>
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
