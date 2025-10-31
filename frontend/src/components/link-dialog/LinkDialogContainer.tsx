import React, { useState, useMemo } from 'react';
import LinkDialogComponent from './LinkDialogComponent';
import { useMatrixBuilder, type MatrixInitialData } from '../../hooks/use-matrix-builder.ts';

export interface LinkableField {
  field_name: string;
  component: string;
  label: string;
  show_if?: Record<string, any[]>;
}

export interface ParentOutput {
  name: string;
  label: string;
  type: string;
  description: string;
  schema?: Record<string, any>;
}

export interface ParentNode {
  parent_id: number;
  parent_name: string;
  parent_node_type: string;
  outputs: ParentOutput[];
}

export interface LinkDialogContainerProps {
  nodeId: number | null;
  nodeName: string;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  linkableField: LinkableField | null;
  parentsOutputs?: ParentNode[];
  currentConfig?: Record<string, any>;
  onSaveLinks?: (links: Record<string, any>) => void;
}

const LinkDialogContainer: React.FC<LinkDialogContainerProps> = ({
  nodeId,
  nodeName,
  isOpen,
  onOpenChange,
  linkableField,
  parentsOutputs = [],
  currentConfig = {},
  onSaveLinks,
}) => {
  const [loading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNodeType, setSelectedNodeType] = useState<string>('all');

  // Get initial data from current configuration using the hook's processInitialData function
  const getInitialData = useMemo((): MatrixInitialData | undefined => {
    console.log('getInitialData called with:', { linkableField, currentConfig });
    if (linkableField && currentConfig[linkableField.field_name]) {
      const configValue = currentConfig[linkableField.field_name];
      console.log('Found config value:', configValue);
      if (Array.isArray(configValue)) {
        // If it's an array of arrays (the format we save), convert to matrix format
        const result = {
          matrix: configValue,
          columns: Array.from({ length: configValue[0]?.length || 2 }, (_, i) => `Column ${i + 1}`)
        };
        console.log('Returning initial data:', result);
        return result;
      }
    }
    console.log('No initial data found');
    return undefined;
  }, [linkableField, currentConfig]);

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
    stats,
    exportMatrix,
  } = useMatrixBuilder(2, 2, getInitialData);

  const renderNestedProperties = (schema: Record<string, any>, parentPath: string = '', depth: number = 0, nodeId?: number, nodeName?: string) => {
    return Object.entries(schema).map(([key, value]) => {
      const currentPath = parentPath ? `${parentPath}.${key}` : key;
      const isNestedObject = typeof value === 'object' && value !== null && !Array.isArray(value);
      
      return (
        <div key={currentPath} className={`${depth > 0 ? 'ml-4' : ''}`}>
          <div
            draggable
            onDragStart={(e) => {
              e.stopPropagation();
              e.dataTransfer.setData(
                'application/json',
                JSON.stringify({
                  nodeId: nodeId,
                  nodeName: nodeName,
                  fieldName: currentPath,
                  fieldType: typeof value === 'object' ? JSON.stringify(value) : value,
                  templateValue: `{{ parent_${nodeId || 0}_result.${currentPath} }}`
                })
              );
              e.dataTransfer.effectAllowed = 'copy';
            }}
            className="cursor-grab px-2 py-1 rounded hover:bg-accent/20 text-xs font-medium bg-background border mb-1"
          >
            {key}: {typeof value === 'object' ? 'object' : value}
          </div>
          {isNestedObject && (
            <div className="mt-1">
              {renderNestedProperties(value, currentPath, depth + 1, nodeId, nodeName)}
            </div>
          )}
        </div>
      );
    });
  };

  // Filter parent nodes based on search and type
  const filteredParentNodes = useMemo(() => {
    return parentsOutputs.filter(node => {
      const matchesSearch = searchTerm === '' || 
        node.parent_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.parent_node_type.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = selectedNodeType === 'all' || node.parent_node_type === selectedNodeType;
      
      return matchesSearch && matchesType;
    });
  }, [parentsOutputs, searchTerm, selectedNodeType]);

  const nodeTypes = useMemo(() => {
    const types = [...new Set(parentsOutputs.map(node => node.parent_node_type))];
    return ['all', ...types];
  }, [parentsOutputs]);


  const handleSaveLinks = (matrixData: { columns: string[], values: (string | object)[][] }) => {
    if (onSaveLinks && linkableField) {
      onSaveLinks({
        [linkableField.field_name]: matrixData.values
      });
    }
    onOpenChange(false);
  };

  const handleSaveLinksClick = () => {
    const matrixData = exportMatrix();
    handleSaveLinks(matrixData);
  };

  return (
    <LinkDialogComponent
      nodeId={nodeId}
      nodeName={nodeName}
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      parentNodes={filteredParentNodes}
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
      onSaveLinks={handleSaveLinksClick}
      searchTerm={searchTerm}
      setSearchTerm={setSearchTerm}
      selectedNodeType={selectedNodeType}
      setSelectedNodeType={setSelectedNodeType}
      nodeTypes={nodeTypes}
      renderNestedProperties={renderNestedProperties}
      filledCells={stats.filledCells}
      totalCells={stats.totalCells}
    />
  );
};

export default LinkDialogContainer;
