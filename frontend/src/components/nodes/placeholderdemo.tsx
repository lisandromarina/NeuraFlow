import { memo } from "react";
import { PlaceholderNode } from "@/components/nodes/placeholder-node";
 
const PlaceholderNodeDemo = memo(() => {
  return (
    <PlaceholderNode>
      <div>+</div>
    </PlaceholderNode>
  );
});
 
export default PlaceholderNodeDemo;