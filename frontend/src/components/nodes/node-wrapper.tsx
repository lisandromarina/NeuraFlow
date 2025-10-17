// src/components/nodes/node-wrapper.tsx
import React from "react";

interface NodeWrapperProps {
  label?: string;
  children: React.ReactNode;
}

export const NodeWrapper: React.FC<NodeWrapperProps> = ({ label, children }) => {
  return (
    <div className="flex flex-col items-center">
      {children}
      {label && <div className="text-xs text-gray-500 mt-1">{label}</div>}
    </div>
  );
};
