import React, { useState } from "react";
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
  SidebarHeader
} from "@/components/ui/sidebar";

import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from "../ui/dropdown-menu";

import { 
  ChevronUp, 
  User2, 
  Plus, 
  Trash2, 
  Play, 
  Pause,
  MoreHorizontal,
  ChevronRight
} from "lucide-react";
import { useWorkflow } from "@/context/WorkflowContext";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";

interface Node {
  id: number;
  title: string;
  type: string;
  category: string;
}

interface WorkflowType {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  user_id: number;
}

interface AppSidebarProps {
  nodes: Node[];
  workflows: WorkflowType[];
  onWorkflowCreate: (name: string, description: string) => Promise<void>;
  onWorkflowDelete: (id: number) => Promise<void>;
  onWorkflowToggle: (id: number) => Promise<void>;
}

export function AppSidebar({ 
  nodes = [], 
  workflows = [],
  onWorkflowCreate,
  onWorkflowDelete,
  onWorkflowToggle
}: AppSidebarProps) {
  const { logout } = useAuth();
  const { selectedWorkflowId, setSelectedWorkflowId } = useWorkflow();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState("");
  const [newWorkflowDescription, setNewWorkflowDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const [isWorkflowsExpanded, setIsWorkflowsExpanded] = useState(true);
  const [isNodesExpanded, setIsNodesExpanded] = useState(true);

  const onLogout = () => logout();

  const handleCreate = async () => {
    if (!newWorkflowName.trim()) return;
    
    setIsLoading(true);
    try {
      await onWorkflowCreate(newWorkflowName, newWorkflowDescription);
      setNewWorkflowName("");
      setNewWorkflowDescription("");
      setIsCreateDialogOpen(false);
    } catch (error) {
      console.error("Failed to create workflow:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedWorkflowId) return;
    
    setIsLoading(true);
    try {
      await onWorkflowDelete(selectedWorkflowId);
      setIsDeleteDialogOpen(false);
    } catch (error) {
      console.error("Failed to delete workflow:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async () => {
    if (!selectedWorkflowId) return;
    
    try {
      await onWorkflowToggle(selectedWorkflowId);
    } catch (error) {
      console.error("Failed to toggle workflow:", error);
    }
  };

  const onDragStart = (event: React.DragEvent, node: Node) => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify({
        type: node.type,
        category: node.category,
        title: node.title,
        id: node.id
      })
    );
    event.dataTransfer.effectAllowed = "move";
  };

  const selectedWorkflow = workflows.find((wf) => wf.id === selectedWorkflowId);

  return (
    <>
      <Sidebar>
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <div className="px-2 py-1">
                {/* Workflows Header */}
                <div 
                  className="flex items-center justify-between mb-2 cursor-pointer hover:bg-accent/50 rounded-md px-2 py-1.5 -mx-2"
                  onClick={() => setIsWorkflowsExpanded(!isWorkflowsExpanded)}
                >
                  <div className="flex items-center gap-2">
                    <ChevronRight 
                      className={`h-4 w-4 transition-transform ${isWorkflowsExpanded ? 'rotate-90' : ''}`}
                    />
                    <SidebarGroupLabel className="text-xs uppercase cursor-pointer">
                      Workflows
                    </SidebarGroupLabel>
                    <Badge variant="outline" className="h-4 text-[10px] px-1">
                      {workflows.length}
                    </Badge>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-6 w-6 p-0 opacity-60 hover:opacity-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsCreateDialogOpen(true);
                    }}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                
                {/* Workflows List */}
                {isWorkflowsExpanded && (
                  <div className="space-y-1 mt-2">
                    {workflows.length === 0 ? (
                      <div className="text-xs text-muted-foreground py-2 text-center">
                        No workflows yet
                      </div>
                    ) : (
                      workflows.map((wf) => (
                        <div
                          key={wf.id}
                          className={`group flex items-center gap-2 rounded-md py-1.5 text-sm cursor-pointer transition-all ${
                            wf.id === selectedWorkflowId 
                              ? 'bg-primary/10  pl-2 pr-2 shadow-sm' 
                              : 'hover:bg-accent/50  px-2'
                          }`}
                          onClick={() => setSelectedWorkflowId(wf.id)}
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="truncate font-medium">{wf.name}</span>
                              {wf.is_active && (
                                <Badge variant="default" className="h-4 text-[10px] px-1">
                                  Active
                                </Badge>
                              )}
                            </div>
                            {wf.description && (
                              <div className="text-xs text-muted-foreground truncate">
                                {wf.description}
                              </div>
                            )}
                          </div>
                          
                          {wf.id === selectedWorkflowId && (
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                                <Button 
                                  variant="ghost" 
                                  size="sm" 
                                  className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100"
                                >
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={(e) => {
                                  e.stopPropagation();
                                  handleToggle();
                                }}>
                                  {wf.is_active ? (
                                    <>
                                      <Pause className="h-4 w-4 mr-2" />
                                      Pause
                                    </>
                                  ) : (
                                    <>
                                      <Play className="h-4 w-4 mr-2" />
                                      Activate
                                    </>
                                  )}
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem 
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setIsDeleteDialogOpen(true);
                                  }}
                                  className="text-destructive focus:text-destructive"
                                >
                                  <Trash2 className="h-4 w-4 mr-2" />
                                  Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          {/* Nodes Header */}
          <div 
            className="flex items-center gap-2 px-4 py-2 cursor-pointer hover:bg-accent/50 rounded-md"
            onClick={() => setIsNodesExpanded(!isNodesExpanded)}
          >
            <ChevronRight 
              className={`h-4 w-4 transition-transform ${isNodesExpanded ? 'rotate-90' : ''}`}
            />
            <SidebarGroupLabel className="cursor-pointer">Nodes</SidebarGroupLabel>
            <Badge variant="outline" className="h-4 text-[10px] px-1">
              {nodes.length}
            </Badge>
          </div>
          
          {/* Nodes List */}
          {isNodesExpanded && (
            <SidebarGroupContent>
              <SidebarMenu>
                {nodes.map((node) => (
                  <SidebarMenuItem key={node.id}>
                  <SidebarMenuButton asChild>
                    <div
                      draggable
                      onDragStart={(e) => onDragStart(e, node)}
                      className="flex items-center gap-2 p-2 cursor-move hover:bg-primary/10 hover:border-l-2 hover:border-l rounded transition-all"
                    >
                      <span>{node.title}</span>
                    </div>
                  </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          )}
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
              <DropdownMenuContent side="top" className="w-[--radix-popper-anchor-width]">
                <DropdownMenuItem><span>Account</span></DropdownMenuItem>
                <DropdownMenuItem><span>Billing</span></DropdownMenuItem>
                <DropdownMenuItem> Theme <ThemeModeToggle /></DropdownMenuItem>
                <DropdownMenuItem onClick={onLogout}><span>Sign out</span></DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>

    {/* Create Workflow Dialog */}
    <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Workflow</DialogTitle>
          <DialogDescription>
            Create a new workflow to automate your tasks.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              placeholder="My Awesome Workflow"
              value={newWorkflowName}
              onChange={(e) => setNewWorkflowName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && newWorkflowName.trim()) {
                  handleCreate();
                }
              }}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Describe what this workflow does..."
              value={newWorkflowDescription}
              onChange={(e) => setNewWorkflowDescription(e.target.value)}
              rows={3}
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setIsCreateDialogOpen(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            disabled={!newWorkflowName.trim() || isLoading}
          >
            {isLoading ? "Creating..." : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    {/* Delete Workflow Confirmation */}
    <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Workflow?</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently delete "{selectedWorkflow?.name}" and all its nodes and connections.
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            disabled={isLoading}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isLoading ? "Deleting..." : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </>
  );
}
