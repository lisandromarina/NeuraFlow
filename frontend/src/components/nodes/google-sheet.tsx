import React, { memo } from "react";
import { Position } from "@xyflow/react";

import { BaseHandle } from "@/components/nodes/base-handle";
import { BaseNode, BaseNodeContent } from "@/components/nodes/base-node";
import { FileSpreadsheet } from "lucide-react";
import { NodeWrapper } from "./node-wrapper";

interface GoogleSheetsNodeProps {
  data: {
    content: string;
    actualType?: string;
    [key: string]: any;
  };
}

const GoogleSheetsNode: React.FC<GoogleSheetsNodeProps> = memo(({ data }) => {
  return (
     <NodeWrapper label={data.actualType}>
      <BaseNode>
        <BaseNodeContent className="flex items-center gap-2">
          <BaseHandle id="target-1" type="target" position={Position.Left} />

          <FileSpreadsheet className="w-5 h-5 text-blue-500" />

          <BaseHandle id="source-1" type="source" position={Position.Right} />
        </BaseNodeContent>
      </BaseNode>
    </NodeWrapper>
  );
});

export default GoogleSheetsNode;
