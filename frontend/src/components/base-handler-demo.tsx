import React, { memo } from "react";
import { Position } from "@xyflow/react";

import { BaseHandle } from "@/components/base-handle";
import { BaseNode, BaseNodeContent } from "@/components/base-node";
 
const BaseHandleDemo = memo(() => {
  return (
    <BaseNode>
      <BaseNodeContent>
        {/* Input handle */}
        <BaseHandle id="target-1" type="target" position={Position.Top} />
        <div>Node Content</div>
        {/* Output handle */}
        <BaseHandle id="source-1" type="source" position={Position.Bottom} />
      </BaseNodeContent>
    </BaseNode>
  );
});
 
export default BaseHandleDemo;