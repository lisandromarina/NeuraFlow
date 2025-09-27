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

export function AppSidebar() {
  return (
    <Sidebar className="bg-neutral-100 border-neutral-300" >
      <SidebarContent>
        <SidebarGroup >
          <ThemeModeToggle />
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
            <SidebarGroupLabel>Chats</SidebarGroupLabel>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}