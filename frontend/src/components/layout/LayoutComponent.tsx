import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "../ui/app-sidebar"

import Workflow from "../workflow";

export default function LayoutComponent() {
  return (
    <SidebarProvider className="bg-background">
        <AppSidebar />
        <SidebarTrigger className="p-auto"/>
        <main className="w-full vh-full">
           <Workflow/>
        </main>
    </SidebarProvider>
  )
}