import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "../ui/app-sidebar"

export default function LayoutComponent() {
  return (
    <SidebarProvider className="bg-background">
        <AppSidebar />
        <SidebarTrigger className="p-auto"/>
        <main className="w-full">
            <p>HOLA</p>
        </main>
    </SidebarProvider>
  )
}