import React from 'react';

export interface JSONNodeProps {
  data: any;
  path?: string;
  nodeId: number;
  nodeName: string;
}

const JSONNode: React.FC<JSONNodeProps> = ({ data, path = '', nodeId, nodeName }) => {
  if (typeof data !== 'object' || data === null) {
    return (
      <div
        draggable
        onDragStart={(e) => {
          e.stopPropagation();
          e.dataTransfer.setData(
            'application/json',
            JSON.stringify({ nodeId, nodeName, fieldName: path, currentValue: data })
          );
          e.dataTransfer.effectAllowed = 'copy';
        }}
        className="cursor-grab px-2 py-1 border rounded mb-1 bg-background hover:bg-accent/20 text-xs"
      >
        {path}: {String(data)}
      </div>
    );
  }

  return (
    <div className="ml-2 border-l pl-2">
      {Object.entries(data).map(([key, value]) => {
        const childPath = path ? `${path}.${key}` : key;
        const isLeaf = typeof value !== 'object' || value === null;

        return (
          <div key={childPath}>
            <div
            draggable
            onDragStart={(e) => {
                e.stopPropagation();
                e.dataTransfer.setData(
                'application/json',
                JSON.stringify({
                    nodeId,
                    nodeName,
                    fieldName: childPath,
                    fieldType: typeof value === 'object' ? 'object' : 'string',
                    currentValue: value, // full object included
                })
                );
                e.dataTransfer.effectAllowed = 'copy';
            }}
            className={`cursor-grab px-2 py-1 rounded hover:bg-accent/20 text-xs font-medium ${
                typeof value === 'object' ? 'font-bold' : ''
            }`}
            >
            {key} {typeof value === 'object' ? '{...}' : `: ${value}`}
            </div>

            {!isLeaf && (
              <JSONNode data={value} path={childPath} nodeId={nodeId} nodeName={nodeName} />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default JSONNode;
