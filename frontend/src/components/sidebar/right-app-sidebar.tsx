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

interface RightAppSidebarProps {
  node: any;
}

export function RightAppSidebar({ node }: RightAppSidebarProps) {
  const [values, setValues] = useState<Record<string, any>>({});
  const { callApi } = useApi();

  // Initialize values from node inputs
  useEffect(() => {
    if (!node?.inputs) return;

    const initialValues: Record<string, any> = {};
    for (const input of node.inputs) {
      const key = input.name || input.key;
      initialValues[key] = input.value ?? input.default ?? "";
    }

    setValues(initialValues);
  }, [node]);

  // Handle input changes
  const handleChange = (name: string, value: any) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  // Determine visible inputs based on `show_if` conditions
  const getVisibleInputs = () => {
    if (!node?.inputs) return [];
    return node.inputs.filter((input: any) => {
      if (!input.show_if) return true; // no condition, always show
      const key = Object.keys(input.show_if)[0];
      const allowedValues = input.show_if[key];
      return allowedValues.includes(values[key]);
    });
  };

  const visibleInputs = getVisibleInputs();

  // Reset hidden values when conditions change (like operation change)
  useEffect(() => {
    if (!node?.inputs) return;

    const visibleKeys = visibleInputs.map((input: any) => input.name);
    setValues((prev) => {
      const newValues: Record<string, any> = {};
      for (const key of visibleKeys) {
        newValues[key] = prev[key];
      }
      return { ...prev, ...newValues };
    });
  }, [values.operation, node]); // re-run when `operation` changes

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
      const response = await callApi(`/workflow-nodes/${node.id}`, "PUT", body);
      console.log("Saved node:", response);
    } catch (error) {
      console.error("Failed to save node:", error);
    }
  };

  // Group inputs if they have a "group" property, otherwise default group
  const groupedInputs: Record<string, any[]> = {};
  visibleInputs.forEach((input) => {
    const group = input.group || "General";
    if (!groupedInputs[group]) groupedInputs[group] = [];
    groupedInputs[group].push(input);
  });

  return (
    <Sidebar side="right">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>
            {node ? node.name : "Node Configuration"}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            {node ? (
              <form className="p-2 space-y-4" onSubmit={handleSubmit}>
                {Object.keys(groupedInputs).map((groupName, idx) => (
                  <div key={idx} className="mb-4">
                    <SidebarGroupLabel>{groupName}</SidebarGroupLabel>
                    <SidebarGroupContent>
                      {groupedInputs[groupName].map((input: any, i: number) => (
                        <div key={i} className="flex flex-col mb-3">
                          <label
                            htmlFor={input.name || input.key}
                            className="mb-1 font-medium"
                          >
                            {input.label || input.name || input.key}
                            {input.required && (
                              <span className="text-red-500 ml-1">*</span>
                            )}
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

                <button
                  type="submit"
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Save
                </button>
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
