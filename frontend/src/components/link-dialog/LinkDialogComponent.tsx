import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { Skeleton } from '../ui/skeleton';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Link, Search, Info, HelpCircle, Download, Upload } from 'lucide-react';
import MatrixBuilder from '../ui/matrix_builder';
import type { ParentNode, LinkableField } from './LinkDialogContainer';

interface LinkDialogComponentProps {
  nodeId: number | null;
  nodeName: string;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  parentNodes: ParentNode[];
  loading: boolean;
  matrix: (string | object)[][];
  columns: string[];
  onDropCell: (rowIndex: number, colIndex: number, value: string | object) => void;
  addRow: () => void;
  removeRow: (rowIndex: number) => void;
  addColumn: () => void;
  removeColumn: (colIndex: number) => void;
  onUpdateCell?: (rowIndex: number, colIndex: number, value: string) => void;
  onUpdateColumn?: (colIndex: number, newName: string) => void;
  onSaveLinks?: () => void;
  linkableField: LinkableField | null;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  selectedNodeType: string;
  setSelectedNodeType: (type: string) => void;
  nodeTypes: string[];
  renderNestedProperties: (schema: Record<string, any>, parentPath?: string, depth?: number, nodeId?: number, nodeName?: string) => React.ReactElement[];
  filledCells: number;
  totalCells: number;
}

const LinkDialogComponent: React.FC<LinkDialogComponentProps> = ({
  nodeId,
  nodeName,
  isOpen,
  onOpenChange,
  parentNodes,
  loading,
  matrix,
  columns,
  onDropCell,
  addRow,
  removeRow,
  addColumn,
  removeColumn,
  onUpdateCell,
  onUpdateColumn,
  onSaveLinks,
  linkableField,
  searchTerm,
  setSearchTerm,
  selectedNodeType,
  setSelectedNodeType,
  nodeTypes,
  renderNestedProperties,
  filledCells,
  totalCells,
}) => {
  if (!nodeId) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-6xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Link className="h-5 w-5" />
            Link Parent Values to {nodeName}
            {linkableField && (
              <Badge variant="outline" className="ml-2">
                {linkableField.label}
              </Badge>
            )}
          </DialogTitle>
          <p className="text-sm text-muted-foreground">
            {linkableField 
              ? `Configure the ${linkableField.label} field by dragging values from parent nodes. Component: ${linkableField.component}`
              : 'Drag values from parent nodes and drop them into the matrix below. You can also edit cells directly.'
            }
          </p>
        </DialogHeader>

        <div className="flex-1 flex flex-col overflow-hidden">
            {loading ? (
              <div className="space-y-3 flex-1">
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
              </div>
            ) : parentNodes.length === 0 ? (
              <Card className="flex-1">
                <CardContent className="pt-6 text-center text-sm text-muted-foreground flex flex-col items-center justify-center h-full">
                  <HelpCircle className="h-12 w-12 mb-4 text-muted-foreground/50" />
                  <div className="text-base font-medium mb-2">No parent nodes found</div>
                  <div>Connect nodes to see linkable values</div>
                </CardContent>
              </Card>
            ) : (
              <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-hidden">
                {/* Parent Nodes Panel */}
                <div className="flex flex-col overflow-hidden">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-medium">Parent Nodes</h3>
                    <Badge variant="secondary">{parentNodes.length} nodes</Badge>
                  </div>
                  
                  {/* Search and Filter Controls */}
                  <div className="space-y-3 mb-4">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search nodes..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                    
                    <div className="flex gap-2 flex-wrap">
                      {nodeTypes.map(type => (
                        <Button
                          key={type}
                          size="sm"
                          variant={selectedNodeType === type ? "default" : "outline"}
                          onClick={() => setSelectedNodeType(type)}
                          className="text-xs"
                        >
                          {type === 'all' ? 'All Types' : type}
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Parent Nodes List */}
                  <div className="flex-1 overflow-y-auto border rounded-lg p-3 bg-muted/5 space-y-3">
                    {parentNodes.map((node) => (
                      <Card key={node.parent_id} className="hover:shadow-md transition-shadow">
                        <CardHeader className="pb-3">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-base">{node.parent_name}</CardTitle>
                            <Badge variant="outline" className="text-xs">
                              {node.parent_node_type}
                            </Badge>
                          </div>
                          <CardDescription className="text-xs">
                            Node ID: {node.parent_id}
                          </CardDescription>
                        </CardHeader>
                        <CardContent className="pt-0">
                          <div className="space-y-2">
                            {node.outputs.map((output) => (
                              <div key={output.name} className="space-y-1">
                                <div className="text-sm font-medium text-foreground">
                                  {output.label || output.name}
                                </div>
                                {output.type === 'object' && output.schema ? (
                                  <div className="ml-2 space-y-1">
                                    {renderNestedProperties(output.schema, output.name, 0, node.parent_id, node.parent_name)}
                                  </div>
                                ) : (
                                  <div
                                    draggable
                                    onDragStart={(e) => {
                                      e.stopPropagation();
                                      e.dataTransfer.setData(
                                        'application/json',
                                        JSON.stringify({
                                          nodeId: node.parent_id,
                                          nodeName: node.parent_name,
                                          fieldName: output.name,
                                          fieldType: output.type,
                                          templateValue: `{{ parent_${node.parent_id}_result.${output.name} }}`
                                        })
                                      );
                                      e.dataTransfer.effectAllowed = 'copy';
                                    }}
                                    className="cursor-grab px-2 py-1 rounded hover:bg-accent/20 text-xs font-medium bg-background border"
                                  >
                                    {output.name} ({output.type})
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                    
                    {parentNodes.length === 0 && searchTerm && (
                      <div className="text-center py-8 text-muted-foreground">
                        <Search className="h-8 w-8 mx-auto mb-2" />
                        <div className="text-sm">No nodes found matching "{searchTerm}"</div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Dynamic Component Panel */}
                <div className="flex flex-col overflow-hidden">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-medium">
                      {linkableField?.label || 'Target Matrix'}
                    </h3>
                    <div className="flex items-center gap-2">
                      {linkableField && (
                        <Badge variant="secondary" className="text-xs">
                          {linkableField.component}
                        </Badge>
                      )}
                      <Badge variant="outline" className="text-xs">
                        {filledCells}/{totalCells} filled
                      </Badge>
                      <Badge variant="secondary" className="text-xs">
                        {matrix.length} × {columns.length}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex-1 overflow-auto">
                    {/* Render component based on type - currently only matrixbuilder is supported */}
                    {(!linkableField || linkableField.component === 'matrixbuilder') ? (
                      <MatrixBuilder
                        matrix={matrix}
                        columns={columns}
                        onDropCell={onDropCell}
                        addRow={addRow}
                        removeRow={removeRow}
                        addColumn={addColumn}
                        removeColumn={removeColumn}
                        onUpdateCell={onUpdateCell}
                        onUpdateColumn={onUpdateColumn}
                      />
                    ) : (
                      <Card className="h-full flex items-center justify-center">
                        <CardContent className="text-center">
                          <Info className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                          <p className="text-sm text-muted-foreground">
                            Component type "{linkableField.component}" not yet implemented
                          </p>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                </div>
              </div>
            )}
        </div>

        <Separator className="my-4" />
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Info className="h-3 w-3" />
              <span>Drag values from parent nodes to matrix cells</span>
            </div>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="ghost" className="h-6 px-2">
                <Download className="h-3 w-3 mr-1" />
                Export
              </Button>
              <Button size="sm" variant="ghost" className="h-6 px-2">
                <Upload className="h-3 w-3 mr-1" />
                Import
              </Button>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={onSaveLinks}>
              Save Links
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default LinkDialogComponent;
