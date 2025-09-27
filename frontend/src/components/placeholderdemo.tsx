import { memo } from "react";
import { PlaceholderNode } from "@/components/placeholder-node";
 
const PlaceholderNodeDemo = memo(() => {
  return (
    <PlaceholderNode>
      <div>+</div>
    </PlaceholderNode>
  );
});
 
export default PlaceholderNodeDemo;