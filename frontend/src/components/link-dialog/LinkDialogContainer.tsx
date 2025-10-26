import React, { useState, useCallback, useEffect } from 'react';
import { toast } from 'sonner';
import LinkDialogComponent from './LinkDialogComponent';
import { useMatrixBuilder } from '../../hooks/use-matrix-builder.ts';

export interface LinkableField {
  field_name: string;
  component: string;
  label: string;
  show_if?: Record<string, any[]>;
}

export interface LinkDialogContainerProps {
  nodeId: number | null;
  nodeName: string;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  linkableField: LinkableField | null;
  parentsOutputs?: ParentNode[];
}

export interface ParentOutput {
  name: string;
  type: string;
  description: string;
  schema?: any; // For JSON objects with specific key types
}

export interface ParentNode {
  parent_id: number;
  parent_name: string;
  parent_node_type: string;
  outputs: ParentOutput[];
}

export interface DisplayParentNode {
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
  linkableField,
  parentsOutputs = [],
}) => {
  const [parentNodes, setParentNodes] = useState<DisplayParentNode[]>([]);
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

  // Helper function to create sample data from schema
  const createSampleFromSchema = (schema: any): any => {
    if (typeof schema === 'string') {
      // Simple type mapping
      switch (schema) {
        case 'string': return 'sample string';
        case 'number': return 123;
        case 'boolean': return true;
        case 'object': return { sample: 'object' };
        case 'array': return ['sample', 'array'];
        default: return 'sample value';
      }
    } else if (typeof schema === 'object' && schema !== null) {
      if (schema.type === 'object' && schema.schema) {
        // Nested object with specific schema
        const result: any = {};
        Object.entries(schema.schema).forEach(([key, value]) => {
          result[key] = createSampleFromSchema(value);
        });
        return result;
      } else if (schema.type === 'array' && schema.items) {
        // Array with item schema
        return [createSampleFromSchema(schema.items)];
      } else {
        // Direct object schema
        const result: any = {};
        Object.entries(schema).forEach(([key, value]) => {
          result[key] = createSampleFromSchema(value);
        });
        return result;
      }
    }
    return 'sample value';
  };

  const fetchParentNodes = useCallback(async () => {
    if (!nodeId) return;
    setLoading(true);
    try {
      // Use the real parents_outputs data passed from the parent component
      if (parentsOutputs && parentsOutputs.length > 0) {
        // Transform the parents_outputs data to match the expected format
        const transformedNodes = parentsOutputs.map(parent => ({
          id: parent.parent_id,
          name: parent.parent_name,
          node_type: parent.parent_node_type,
          currentValue: parent.outputs.reduce((acc, output) => {
            // Create sample data based on type and schema
            let sampleValue;
            
            if (output.type === 'object' && output.schema) {
              // Use schema to create realistic sample data
              sampleValue = createSampleFromSchema(output.schema);
            } else if (output.type === 'object') {
              sampleValue = { sample: 'object data' };
            } else if (output.type === 'string') {
              sampleValue = 'sample string';
            } else if (output.type === 'number') {
              sampleValue = 123;
            } else if (output.type === 'array') {
              sampleValue = output.schema ? 
                [createSampleFromSchema(output.schema.items || output.schema)] : 
                ['sample', 'array', 'data'];
            } else {
              sampleValue = 'sample value';
            }
            
            acc[output.name] = {
              type: output.type,
              description: output.description,
              schema: output.schema,
              value: sampleValue
            };
            return acc;
          }, {} as Record<string, any>)
        }));
        setParentNodes(transformedNodes);
      } else {
        // Fallback to empty array if no parents_outputs
        setParentNodes([]);
      }
    } catch (error) {
      console.error(error);
      toast.error('Failed to load parent node data');
    } finally {
      setLoading(false);
    }
  }, [nodeId, parentsOutputs]);

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
      linkableField={linkableField}
    />
  );
};

export default LinkDialogContainer;
