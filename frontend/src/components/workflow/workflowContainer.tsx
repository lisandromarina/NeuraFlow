import React, { useRef, useState } from "react";
import { useNodesState, useEdgesState, addEdge } from "@xyflow/react";
import type { NodeTypes } from "@xyflow/react";
import WorkflowComponent from "./workflowComponent";
import PlaceholderNodeDemo from "../placeholderdemo";
import BaseHandle from "../base-handler-demo";

const nodeTypes: NodeTypes = {
  placeholderNode: PlaceholderNodeDemo,
  baseHandle: BaseHandle
};

const initialNodes = [
  {
    id: "1",
    data: { label: "Original Node" },
    position: { x: 75, y: 0 },
    type: "baseHandle",
  },
  {
    id: "2",
    data: { label: "Original Node" },
    position: { x: 0, y: 150 },
    type: "baseHandle",
  },
  {
    id: "3",
    data: { label: "Original Node" },
    position: { x: 150, y: 150 },
    type: "baseHandle",
  },
];

const initialEdges = [
  {
    id: "1=>2",
    source: "1",
    target: "2",
    sourceHandle: "source-1", // must match the output handle on Node 1
    targetHandle: "target-1", // must match the input handle on Node 2
    type: "simplebezier",     // simplebezier line ensures top->bottom connection
    animated: true,
  },
    {
    id: "2=>3",
    source: "1",
    target: "3",
    sourceHandle: "source-1", // must match the output handle on Node 1
    targetHandle: "target-1", // must match the input handle on Node 2
    type: "simplebezier",     // simplebezier line ensures top->bottom connection
    animated: true,
  },
];

const WorkflowContainer: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // track viewport to account for pan/zoom
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });

  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  const onConnect = (connection: any) => {
    setEdges((eds) => addEdge(connection, eds));
  };

  // Drag over handler
  const onDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  };

  // Drop handler
  const onDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const type = event.dataTransfer.getData("application/reactflow");
    const bounds = reactFlowWrapper.current?.getBoundingClientRect();
    if (!type || !bounds) return;

    // Calculate position accounting for pan/zoom
    const position = {
      x: (event.clientX - bounds.left - viewport.x) / viewport.zoom,
      y: (event.clientY - bounds.top - viewport.y) / viewport.zoom,
    };

    const newNode = {
      id: `${nodes.length + 1}`, // simple incremental ID
      type,
      position,
      data: { label: `${type} ${nodes.length + 1}` },
    };

    setNodes((nds) => [...nds, newNode]);
  };

  return (
    <div
      className="w-full h-full"
      ref={reactFlowWrapper}
      onDrop={onDrop}
      onDragOver={onDragOver}
    >
      <WorkflowComponent
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onInit={(instance) => setViewport(instance.viewport)} // get initial viewport
        onViewportChange={(v) => setViewport(v)} // track pan/zoom
      />
    </div>
  );
};

export default WorkflowContainer;
