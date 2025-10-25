import React, { useState, useCallback, useEffect } from 'react';
import { toast } from 'sonner';
import LinkDialogComponent from './LinkDialogComponent';
import { useMatrixBuilder } from '../../hooks/use-matrix-builder.ts';

export interface LinkDialogContainerProps {
  nodeId: number | null;
  nodeName: string;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export interface ParentNode {
  id: number;
  name: string;
  node_type: string;
  currentValue?: any; // full JSON
}

const LinkDialogContainer: React.FC<LinkDialogContainerProps> = ({
  nodeId,
  nodeName,
  isOpen,
  onOpenChange,
}) => {
  const [parentNodes, setParentNodes] = useState<ParentNode[]>([]);
  const [loading, setLoading] = useState(false);

  const {
    matrix,
    columns,
    addRow,
    removeRow,
    addColumn,
    removeColumn,
    updateCell,
    updateColumn,
    handleDropCell,
  } = useMatrixBuilder(2, 2);

  const fetchParentNodes = useCallback(async () => {
    if (!nodeId) return;
    setLoading(true);
    try {
      const mockData = {
        response: { user: { name: 'Alice', last_name: 'Smith', age: 30 }, status: 'ok' },
        status_code: 200,
        headers: { 'Content-Type': 'application/json' },
      };

      setParentNodes([
        {
          id: 1,
          name: 'HTTP Request Node',
          node_type: 'HttpNode',
          currentValue: mockData,
        },
      ]);
    } catch (error) {
      console.error(error);
      toast.error('Failed to load parent node data');
    } finally {
      setLoading(false);
    }
  }, [nodeId]);

  useEffect(() => {
    if (isOpen && nodeId) fetchParentNodes();
  }, [isOpen, nodeId, fetchParentNodes]);

  return (
    <LinkDialogComponent
      nodeId={nodeId}
      nodeName={nodeName}
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      parentNodes={parentNodes}
      loading={loading}
      matrix={matrix}
      columns={columns}
      onDropCell={handleDropCell}
      addRow={addRow}
      removeRow={removeRow}
      addColumn={addColumn}
      removeColumn={removeColumn}
      onUpdateCell={updateCell}
      onUpdateColumn={updateColumn}
    />
  );
};

export default LinkDialogContainer;
