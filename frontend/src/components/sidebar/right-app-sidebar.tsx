"use client";

import React, { useEffect, useState } from "react";
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

export interface NodeType {
  id: number;
  name: string;
  inputs: NodeInput[];
}

// -------------------- Props --------------------

interface RightAppSidebarProps {
  node: NodeType | null;
}

// -------------------- Component --------------------

export function RightAppSidebar({ node }: RightAppSidebarProps) {
  const { callApi } = useApi();
  const groupedInputs: Record<string, NodeInput[]> = {};

  // Initialize values from node inputs for first render
  const [values, setValues] = useState<Record<string, any>>(() => {
    if (!node?.inputs) return {};
    const initialValues: Record<string, any> = {};
    node.inputs.forEach((input: NodeInput) => {
      initialValues[input.name] = input.value ?? input.default ?? "";
    });
    return initialValues;
  });

  
  // Compute visible inputs based on show_if
  const visibleInputs = node?.inputs.filter((input: NodeInput) => {
    if (!input.show_if) return true;
    const key = Object.keys(input.show_if)[0];
    const allowedValues = input.show_if[key];
    const currentValue =
    values[key] ?? node.inputs.find((i) => i.name === key)?.default;
    return allowedValues.includes(currentValue);
  }) || [];

  // Handle input changes
  const handleChange = (name: string, value: any) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  // Group inputs by `group` property
  visibleInputs.forEach((input: NodeInput) => {
    const group = input.group || "";
    if (!groupedInputs[group]) groupedInputs[group] = [];
    groupedInputs[group].push(input);
  });

  // Submit handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const bodyValues = { ...values };

      // Parse the values field if it's a string
      if (bodyValues.values && typeof bodyValues.values === "string") {
        try {
          bodyValues.values = JSON.parse(bodyValues.values);
        } catch (err) {
          console.error("Invalid JSON in 'values'", err);
          alert("Please enter a valid JSON array for 'values'");
          return;
        }
      }

      const body = { custom_config: bodyValues };
      const response = await callApi(`/workflow-nodes/${node?.id}`, "PUT", body);
      toast.success("Saved node:", response);
      console.log("Configuration Saved!");
    } catch (error) {
      toast.error("Failed to save configuration");
      console.error("Failed to save node:", error);
    }
  };

    // Reset values whenever a new node is selected (keyed by node id)
  useEffect(() => {
    if (!node?.inputs) return;
    const initialValues: Record<string, any> = {};
    node.inputs.forEach((input: NodeInput) => {
      initialValues[input.name] = input.value ?? input.default ?? "";
    });
    setValues(initialValues);
  }, [node?.id]);
  
  // Ensure all visible inputs have a value
  useEffect(() => {
    if (!visibleInputs.length) return;

    setValues((prev) => {
      const updated = { ...prev };
      let hasChanged = false;

      visibleInputs.forEach((input: NodeInput) => {
        if (updated[input.name] === undefined) {
          updated[input.name] = input.value ?? input.default ?? "";
          hasChanged = true;
        }
      });

      return hasChanged ? updated : prev;
    });
  }, [visibleInputs]);

  return (
    <Sidebar side="right">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{node ? node.name : "Node Configuration"}</SidebarGroupLabel>
          <SidebarGroupContent>
            {node ? (
              <form className="p-2 space-y-4" onSubmit={handleSubmit}>
                {Object.keys(groupedInputs).map((groupName, idx) => (
                  <div key={idx} className="mb-4">
                    {groupName && <SidebarGroupLabel>{groupName}</SidebarGroupLabel>}
                    <SidebarGroupContent>
                      {groupedInputs[groupName].map((input: NodeInput, i: number) => (
                        <div key={i} className="flex flex-col mb-3">
                          <label htmlFor={input.name} className="mb-1 font-medium">
                            {input.label || input.name}
                            {input.required && <span className="text-red-500 ml-1">*</span>}
                          </label>
                          <Field
                            input={input}
                            value={values[input.name]}
                            onChange={handleChange}
                          />
                        </div>
                      ))}
                    </SidebarGroupContent>
                  </div>
                ))}

                {visibleInputs.length === 0 && (
                  <SidebarMenuItem>
                    <div className="p-2 text-gray-500">
                      No inputs available for the selected operation.
                    </div>
                  </SidebarMenuItem>
                )}

                <Button type="submit">Save</Button>
              </form>
            ) : (
              <SidebarMenuItem>
                <div className="p-2 text-gray-500">
                  Select a node to see its configuration
                </div>
              </SidebarMenuItem>
            )}
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
