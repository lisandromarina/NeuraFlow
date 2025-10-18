"use client";

import React, { useEffect, useState, useMemo } from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { Field } from "../ui/fields";
import { useApi } from "../../api/useApi";
import { toast } from "sonner";
import { Button } from "../ui/button";

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
  credentials?: NodeCredentials;
  inputs: NodeInput[];
}

// -------------------- Props --------------------

interface RightAppSidebarProps {
  node: NodeType | null;
}

// -------------------- Component --------------------

export function RightAppSidebar({ node }: RightAppSidebarProps) {
  const { callApi } = useApi();

  const [values, setValues] = useState<Record<string, any>>({});
  const [connected, setConnected] = useState(false);

  // Initialize input values whenever a new node is selected
  useEffect(() => {
    if (!node) return;
    const initialValues: Record<string, any> = {};
    node.inputs.forEach((input) => {
      initialValues[input.name] = input.value ?? input.default ?? "";
    });
    setValues(initialValues);
    setConnected(false); // reset credentials status
  }, [node?.id, node?.inputs]);

  // Compute visible inputs based on `show_if`
  const visibleInputs = useMemo(() => {
    if (!node) return [];
    return node.inputs.filter((input) => {
      if (!input.show_if) return true;
      return Object.entries(input.show_if).every(([key, allowedValues]) => {
        const currentValue = values[key] ?? node.inputs.find((i) => i.name === key)?.default;
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
      if (bodyValues.values && typeof bodyValues.values === "string") {
        try {
          bodyValues.values = JSON.parse(bodyValues.values);
        } catch {
          toast.error("Invalid JSON in 'values'");
          return;
        }
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
      <Sidebar side="right">
        <SidebarContent>
          <SidebarMenuItem>
            <div className="p-2 text-gray-500">Select a node to see its configuration</div>
          </SidebarMenuItem>
        </SidebarContent>
      </Sidebar>
    );
  }

  return (
    <Sidebar side="right">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{node.name}</SidebarGroupLabel>
          <SidebarGroupContent>
            {/* Credentials section */}
            {node.credentials && (
              <div className="mb-4 p-2 border rounded">
                <div className="font-medium mb-2">{node.credentials.label}</div>
                <Button onClick={handleConnect} disabled={connected}>
                  {connected ? "Connected" : "Connect Account"}
                </Button>
              </div>
            )}

            {/* Node inputs */}
            <form className="p-2 space-y-4" onSubmit={handleSubmit}>
              {Object.entries(groupedInputs).map(([groupName, inputs], idx) => (
                <div key={idx} className="mb-4">
                  {groupName && <SidebarGroupLabel>{groupName}</SidebarGroupLabel>}
                  <SidebarGroupContent>
                    {inputs.map((input) => (
                      <div key={input.name} className="flex flex-col mb-3">
                        <label htmlFor={input.name} className="mb-1 font-medium">
                          {input.label ?? input.name}
                          {input.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        <Field input={input} value={values[input.name]} onChange={handleChange} />
                      </div>
                    ))}
                  </SidebarGroupContent>
                </div>
              ))}

              {visibleInputs.length === 0 && (
                <SidebarMenuItem>
                  <div className="p-2 text-gray-500">No inputs available for the selected operation.</div>
                </SidebarMenuItem>
              )}

              <Button type="submit">Save</Button>
            </form>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
