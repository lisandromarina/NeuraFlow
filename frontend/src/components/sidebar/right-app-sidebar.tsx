"use client";

import React, { useEffect, useState, useMemo } from "react";
import {
  Sidebar,
  SidebarContent,
  useSidebar,
} from "@/components/ui/sidebar";
import { Field } from "../ui/fields";
import { useApi } from "../../api/useApi";
import { toast } from "sonner";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { CheckCircle2, CircleDot, Save, Settings2 } from "lucide-react";
import { Separator } from "../ui/separator";

// -------------------- Type Definitions --------------------

export interface NodeInput {
  name: string;
  label?: string;
  type: string;
  value?: any;
  default?: any;
  required?: boolean;
  options?: { label: string; value: any }[];
  show_if?: Record<string, any[]>;
  group?: string;
  placeholder?: string;
  description?: string;
}

export interface NodeCredentials {
  required?: boolean;
  type: string;
  label: string;
  endpoint: string;
  scopes?: string[];
}

export interface NodeType {
  id: number;
  name: string;
  node_type?: string;
  credentials?: NodeCredentials;
  inputs: NodeInput[];
  hasCredentials: boolean
}

// -------------------- Props --------------------

interface RightAppSidebarProps {
  node: NodeType | null;
}

// -------------------- Component --------------------

export function RightAppSidebar({ node }: RightAppSidebarProps) {
  const { callApi } = useApi();
  const { open, openMobile, setOpen, setOpenMobile, isMobile } = useSidebar();

  const [values, setValues] = useState<Record<string, any>>({});
  const [connected, setConnected] = useState(false);

  // Sync mobile state with desktop state when open changes
  useEffect(() => {
    if (isMobile && open) {
      setOpenMobile(true);
    }
  }, [open, isMobile, setOpenMobile]);

  // Sync desktop state when mobile sheet closes
  useEffect(() => {
    if (isMobile && !openMobile && open) {
      setOpen(false);
    }
  }, [openMobile, open, isMobile, setOpen]);

  // Initialize input values whenever a new node is selected
  useEffect(() => {
    if (!node) return;
    const initialValues: Record<string, any> = {};
    node.inputs.forEach((input) => {
      // Use the value from the backend (which includes saved custom_config values)
      // Fall back to default if no value is set
      // For select fields, don't use empty string as it won't match show_if conditions
      const value = input.value ?? input.default;
      if (value !== undefined && value !== null) {
        initialValues[input.name] = value;
      }
    });
    setValues(initialValues);

    // Set connected based on backend
    setConnected(node.hasCredentials ?? false);
  }, [node?.id, node?.inputs, node?.credentials]);

  // Compute visible inputs based on `show_if`
  const visibleInputs = useMemo(() => {
    if (!node) return [];
    
    return node.inputs.filter((input) => {
      // If no show_if condition, always show the input
      if (!input.show_if) return true;
      
      // Check all show_if conditions
      return Object.entries(input.show_if).every(([key, allowedValues]) => {
        // Get the current value from the state first (this is what the user has selected)
        let currentValue = values[key];
        
        // If not in state, check the input definition
        if (currentValue === undefined || currentValue === null || currentValue === "") {
          const inputDef = node.inputs.find((i) => i.name === key);
          currentValue = inputDef?.value;
          // Only use default if value is also not set
          if (currentValue === undefined || currentValue === null || currentValue === "") {
            currentValue = inputDef?.default;
          }
        }
        
        // Handle empty/null/undefined values - they won't match any show_if condition
        if (currentValue === undefined || currentValue === null || currentValue === "") {
          return false;
        }
        
        return allowedValues.includes(currentValue);
      });
    });
  }, [node, values]);

  // Group inputs by their `group` property
  const groupedInputs = useMemo(() => {
    const groups: Record<string, NodeInput[]> = {};
    visibleInputs.forEach((input) => {
      const groupName = input.group ?? "";
      if (!groups[groupName]) groups[groupName] = [];
      groups[groupName].push(input);
    });
    return groups;
  }, [visibleInputs]);

  const handleChange = (name: string, value: any) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleConnect = () => {
    if (!node?.credentials) return;
    console.log(node?.credentials)

    callApi(node.credentials.endpoint + `/connect`, "POST", {
      user_id:1,
      scopes: node.credentials.scopes,
      provider: node.credentials.type
    })
      .then((res: { oauth_url: string }) => {
        const width = 600;
        const height = 700;
        const left = window.screen.width / 2 - width / 2;
        const top = window.screen.height / 2 - height / 2;

        const popup = window.open(
          res.oauth_url,
          "oauthPopup",
          `width=${width},height=${height},top=${top},left=${left}`
        );

        if (!popup) {
          toast.error("Popup blocked! Please allow popups for this site.");
          return;
        }

        const handleMessage = (event: MessageEvent) => {
          if (event.origin !== window.location.origin) return;

          const { success, message } = event.data;
          if (success) {
            toast.success(message);
            setConnected(true);
          } else {
            toast.error(message || "OAuth failed");
          }

          window.removeEventListener("message", handleMessage);
        };

        window.addEventListener("message", handleMessage);
      })
      .catch((err) => {
        toast.error("Failed to start OAuth flow");
        console.error(err);
      });
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (node?.credentials?.required && !connected) {
      toast.error("Please connect your account first");
      return;
    }

    try {
      const bodyValues = { ...values };
      
      // Parse JSON fields
      if (node) {
        node.inputs.forEach((input) => {
          if (input.type === "json" && bodyValues[input.name] && typeof bodyValues[input.name] === "string") {
            try {
              bodyValues[input.name] = JSON.parse(bodyValues[input.name]);
            } catch {
              toast.error(`Invalid JSON in '${input.label || input.name}'`);
              return;
            }
          }
        });
      }

      const body = { custom_config: bodyValues };
      const response = await callApi(`/workflow-nodes/${node?.id}`, "PUT", body);
      toast.success("Node configuration saved!");
      console.log("Saved:", response);
    } catch (err) {
      toast.error("Failed to save configuration");
      console.error(err);
    }
  };

  if (!node) {
    return (
      <Sidebar side="right" className="border-l">
        <SidebarContent className="p-6">
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center">
              <Settings2 className="w-8 h-8 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-1">No Node Selected</h3>
              <p className="text-sm text-muted-foreground">
                Select a node from the workflow to view and edit its configuration
              </p>
            </div>
          </div>
        </SidebarContent>
      </Sidebar>
    );
  }

  return (
    <Sidebar side="right" className="border-l">
      <SidebarContent key={node.id} className="p-0">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-background border-b">
          <div className="p-6 pb-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h2 className="text-xl font-semibold tracking-tight mb-1">{node.name}</h2>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    {node.node_type}
                  </Badge>
                  <span className="text-xs text-muted-foreground">ID: {node.id}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6 pt-4 space-y-6">
            {/* Credentials section */}
            {node.credentials && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    {connected ? (
                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                    ) : (
                      <CircleDot className="w-4 h-4 text-muted-foreground" />
                    )}
                    {node.credentials.label}
                  </CardTitle>
                  <CardDescription className="text-xs">
                    {connected ? "Account connected successfully" : "Connect your account to use this node"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pb-4">
                  <Button 
                    onClick={handleConnect} 
                    disabled={connected}
                    variant={connected ? "outline" : "default"}
                    className="w-full"
                    size="sm"
                  >
                    {connected ? "Connected" : "Connect Account"}
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Node Configuration Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {Object.entries(groupedInputs).map(([groupName, inputs], idx) => (
                <div key={idx}>
                  {groupName && (
                    <>
                      <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                        {groupName}
                      </h3>
                    </>
                  )}
                  <div className="space-y-4">
                    {inputs.map((input) => (
                      <div key={input.name} className="space-y-2">
                        <label 
                          htmlFor={input.name} 
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-1"
                        >
                          {input.label ?? input.name}
                          {input.required && <span className="text-destructive">*</span>}
                        </label>
                        {input.description && (
                          <p className="text-xs text-muted-foreground">{input.description}</p>
                        )}
                        <Field input={input} value={values[input.name]} onChange={handleChange} />
                      </div>
                    ))}
                  </div>
                  {idx < Object.entries(groupedInputs).length - 1 && (
                    <Separator className="mt-6" />
                  )}
                </div>
              ))}

              {visibleInputs.length === 0 && !node.credentials && (
                <Card>
                  <CardContent className="pt-6">
                    <p className="text-sm text-muted-foreground text-center">
                      No configuration options available for this node.
                    </p>
                  </CardContent>
                </Card>
              )}
            </form>
          </div>
        </div>

        {/* Footer with Save Button */}
        <div className="sticky bottom-0 bg-background border-t p-4">
          <Button 
            onClick={handleSubmit} 
            className="w-full"
            size="default"
          >
            <Save className="w-4 h-4 mr-2" />
            Save Configuration
          </Button>
        </div>
      </SidebarContent>
    </Sidebar>
  );
}
