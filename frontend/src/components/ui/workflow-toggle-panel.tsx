import React from "react";
import { Panel } from "@xyflow/react";
import { Label } from "@radix-ui/react-label";
import { Switch } from "../ui/switch";

interface WorkflowTogglePanelProps {
  workflowActive: boolean;
  onToggle: () => void;
}

const WorkflowTogglePanel: React.FC<WorkflowTogglePanelProps> = ({
  workflowActive,
  onToggle,
}) => {
  return (
    <Panel
      className="flex items-center justify-between gap-2 rounded-lg bg-secondary p-3 text-foreground shadow-md min-w-[180px]"
      position="bottom-center"
      style={{ bottom: 40 }}
    >
      <div className="flex flex-col">
        <Label htmlFor="workflow-toggle" className="text-sm font-medium">
          Workflow
        </Label>
        <span
          className={`text-xs font-semibold mt-1 ${
            workflowActive ? "text-green-500" : "text-red-500"
          }`}
        >
          {workflowActive ? "Active" : "Inactive"}
        </span>
      </div>
      <Switch
        id="workflow-toggle"
        checked={workflowActive}
        onCheckedChange={onToggle}
      />
    </Panel>
  );
};

export default WorkflowTogglePanel;
