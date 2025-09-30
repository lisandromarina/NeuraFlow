import React from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar";

interface RightAppSidebarProps {
  node: any;
}

export function RightAppSidebar({ node }: RightAppSidebarProps) {
  const renderInputField = (input: any, index: number) => {
    const value = input.value ?? input.default ?? "";
    const commonProps = {
      id: input.name || input.key || `input-${index}`,
      defaultValue: value,
      required: !!input.required,
      className: "w-full border p-1 rounded",
    };

    switch (input.type) {
      case "number":
        return <input type="number" {...commonProps} />;
      case "textarea":
        return <textarea {...commonProps} rows={3} />;
      case "select":
        return (
          <select {...commonProps}>
            {input.options?.map((option: any, idx: number) => (
              <option key={idx} value={option.value ?? option}>
                {option.label ?? option}
              </option>
            ))}
          </select>
        );
      case "checkbox":
        return (
          <input
            type="checkbox"
            id={commonProps.id}
            defaultChecked={!!value}
            required={commonProps.required}
            className="mr-2"
          />
        );
      default: // default to text input
        return <input type="text" {...commonProps} />;
    }
  };

  return (
    <Sidebar side="right">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{node ? node.name : "Node Configuration"}</SidebarGroupLabel>
          <SidebarGroupContent>
            {node ? (
              <div className="p-2 space-y-4">
                {node.inputs && node.inputs.length > 0 ? (
                  node.inputs.map((input: any, index: number) => (
                    <div key={index} className="flex flex-col">
                      <label
                        htmlFor={input.name || input.key || `input-${index}`}
                        className="mb-1 font-medium"
                      >
                        {input.label || input.name || input.key}
                        {input.required && <span className="text-red-500 ml-1">*</span>}
                      </label>
                      {renderInputField(input, index)}
                    </div>
                  ))
                ) : (
                  <SidebarMenuItem>
                    <div className="p-2 text-gray-500">
                      No inputs available for this node.
                    </div>
                  </SidebarMenuItem>
                )}
              </div>
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
