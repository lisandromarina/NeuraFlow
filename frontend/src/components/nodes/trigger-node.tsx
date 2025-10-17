import React, { memo } from "react";
import { Position } from "@xyflow/react";

import { BaseHandle } from "@/components/nodes/base-handle";
import { BaseNode, BaseNodeContent } from "@/components/nodes/base-node";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ClockPlus } from "lucide-react";
import { NodeWrapper } from "./node-wrapper";


interface TriggerNodeProps {
  data: {
    content: string;
    [key: string]: any;
  };
}

const TriggerNode: React.FC<TriggerNodeProps> = memo(({ data }) => {
  return (
    <NodeWrapper label={data.actualType}>
      <BaseNode>
        <BaseNodeContent>
          <div className="flex items-center gap-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <ClockPlus className="w-5 h-5 text-blue-500 cursor-pointer" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>{data.actualType}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <BaseHandle id="source-1" type="source" position={Position.Right} />
        </BaseNodeContent>
      </BaseNode>
    </NodeWrapper>
  );
});

export default TriggerNode;
