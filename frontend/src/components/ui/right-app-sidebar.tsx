import React, { useEffect, useState } from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { Field } from "./fields";
import { useApi } from "../../api/useApi";

interface RightAppSidebarProps {
  node: any;
}

export function RightAppSidebar({ node }: RightAppSidebarProps) {
  const [values, setValues] = useState<Record<string, any>>({});
  const { callApi } = useApi();
  

  useEffect(() => {
    if (!node?.inputs) return;

    const initialValues: Record<string, any> = {};
    for (const input of node.inputs) {
      const key = input.name || input.key;
      initialValues[key] = input.value ?? input.default ?? "";
    }

    setValues(initialValues);
  }, [node]);

  const handleChange = (name: string, value: any) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const createBody = () => {
    return {
      "custom_config": values
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    let body = createBody()

    try {
      const response = await callApi(
        `/workflow-nodes/${node.id}`, 
        "PUT",
        body                        
      );

      console.log("Saved node:", response);
    } catch (error) {
      console.error("Failed to save node:", error);
    }
  };

  return (
    <Sidebar side="right">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>
            {node ? node.name : "Node Configuration"}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            {node ? (
              <form
                className="p-2 space-y-4"
                onSubmit={handleSubmit}
              >
                {node.inputs && node.inputs.length > 0 ? (
                  node.inputs.map((input: any, index: number) => (
                    <div key={index} className="flex flex-col">
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
                  ))
                ) : (
                  <SidebarMenuItem>
                    <div className="p-2 text-gray-500">
                      No inputs available for this node.
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
