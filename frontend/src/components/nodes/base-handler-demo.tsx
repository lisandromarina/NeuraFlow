import React, { memo } from "react";
import { Position } from "@xyflow/react";

import { BaseHandle } from "@/components/nodes/base-handle";
import { BaseNode, BaseNodeContent } from "@/components/nodes/base-node";

interface BaseHandleDemoProps {
  data: {
    content: string;
    [key: string]: any;
  };
}

const BaseHandleDemo: React.FC<BaseHandleDemoProps> = memo(({ data  }) => {
  return (
    <BaseNode>
      <BaseNodeContent>
        {/* Input handle */}
        <BaseHandle id="target-1" type="target" position={Position.Top} />
        {/* Display content from prop */}
        <div>{data.actualType}</div>
        {/* Output handle */}
        <BaseHandle id="source-1" type="source" position={Position.Bottom} />
      </BaseNodeContent>
    </BaseNode>
  );
});

export default BaseHandleDemo;
