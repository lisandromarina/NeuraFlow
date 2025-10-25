import React, { useState, useRef, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Plus, X, GripVertical, Edit3, Check, X as XIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

interface MatrixBuilderProps {
  matrix: (string | object)[][]; // allow objects in cells
  columns: string[];
  onDropCell: (rowIndex: number, colIndex: number, value: string | object) => void;
  addRow: () => void;
  removeRow: (rowIndex: number) => void;
  addColumn: () => void;
  removeColumn: (colIndex: number) => void;
  onUpdateColumn?: (colIndex: number, newName: string) => void;
  onUpdateCell?: (rowIndex: number, colIndex: number, value: string) => void; // editing only strings
}

const MatrixBuilder: React.FC<MatrixBuilderProps> = ({
  matrix,
  columns,
  onDropCell,
  addRow,
  removeRow,
  addColumn,
  removeColumn,
  onUpdateColumn,
  onUpdateCell,
}) => {
  const [draggedOver, setDraggedOver] = useState<{ row: number; col: number } | null>(null);
  const [editingCell, setEditingCell] = useState<{ row: number; col: number } | null>(null);
  const [editingColumn, setEditingColumn] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if ((editingCell || editingColumn !== null) && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editingCell, editingColumn]);

  const handleDragOver = (e: React.DragEvent, rowIndex: number, colIndex: number) => {
    e.preventDefault();
    setDraggedOver({ row: rowIndex, col: colIndex });
  };

  const handleDragLeave = () => {
    setDraggedOver(null);
  };

  const handleDrop = (e: React.DragEvent, rowIndex: number, colIndex: number) => {
    e.preventDefault();
    setDraggedOver(null);

    try {
      const data = e.dataTransfer.getData('application/json');
      if (data) {
        const parsed = JSON.parse(data);
        onDropCell(rowIndex, colIndex, parsed.currentValue || parsed);
      } else {
        const text = e.dataTransfer.getData('text');
        onDropCell(rowIndex, colIndex, text);
      }
    } catch (error) {
      console.error('Error parsing dropped data:', error);
    }
  };

  const handleCellClick = (rowIndex: number, colIndex: number) => {
    const cell = matrix[rowIndex][colIndex];
    if (onUpdateCell && typeof cell === 'string') {
      setEditingCell({ row: rowIndex, col: colIndex });
      setEditValue(cell);
    }
  };

  const handleCellEdit = () => {
    if (editingCell && onUpdateCell) {
      onUpdateCell(editingCell.row, editingCell.col, editValue);
      setEditingCell(null);
      setEditValue('');
    }
  };

  const handleColumnEdit = () => {
    if (editingColumn !== null && onUpdateColumn) {
      onUpdateColumn(editingColumn, editValue);
      setEditingColumn(null);
      setEditValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (editingCell) handleCellEdit();
      if (editingColumn !== null) handleColumnEdit();
    } else if (e.key === 'Escape') {
      setEditingCell(null);
      setEditingColumn(null);
      setEditValue('');
    }
  };

  return (
    <div className="flex flex-col gap-3 overflow-auto p-4 border rounded-lg bg-muted/5">
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-muted-foreground">Matrix Builder</h3>
          <Badge variant="secondary" className="text-xs">
            {matrix.length} × {columns.length}
          </Badge>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={addRow} className="h-8">
            <Plus className="h-3 w-3 mr-1" />
            Row
          </Button>
          <Button size="sm" variant="outline" onClick={addColumn} className="h-8">
            <Plus className="h-3 w-3 mr-1" />
            Column
          </Button>
        </div>
      </div>

      {/* Column headers */}
      <div className="flex items-center gap-2">
        {/* Empty space for alignment with row actions */}
        <div className="w-8 h-8"></div>
        
        {/* Column headers */}
        <div className="flex-1 grid gap-2" style={{ gridTemplateColumns: `repeat(${columns.length}, minmax(120px, 1fr))` }}>
          {columns.map((col, colIndex) => (
            <div key={colIndex} className="relative group">
              {editingColumn === colIndex ? (
                <div className="flex items-center gap-1">
                  <Input
                    ref={inputRef}
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onBlur={handleColumnEdit}
                    className="h-8 text-xs"
                    placeholder="Column name"
                  />
                  <Button size="sm" variant="ghost" onClick={handleColumnEdit} className="h-6 w-6 p-0">
                    <Check className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setEditingColumn(null)}
                    className="h-6 w-6 p-0"
                  >
                    <XIcon className="h-3 w-3" />
                  </Button>
                </div>
              ) : (
                <div className="flex items-center justify-between bg-background border rounded-md px-3 py-2 text-sm font-medium group-hover:bg-accent/10 transition-colors">
                  <span className="truncate">{col}</span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {onUpdateColumn && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setEditingColumn(colIndex);
                          setEditValue(col);
                        }}
                        className="h-6 w-6 p-0"
                      >
                        <Edit3 className="h-3 w-3" />
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeColumn(colIndex)}
                      className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
        
        {/* Empty space for alignment with row actions */}
        <div className="w-8 h-8"></div>
      </div>

      {/* Matrix rows */}
      <div className="space-y-2">
        {matrix.map((row, rowIndex) => (
          <div key={rowIndex} className="group">
            <div className="flex items-center gap-2">
              {/* Empty space for alignment */}
              <div className="w-8 h-8"></div>
              
              {/* Data cells */}
              <div className="flex-1 grid gap-2" style={{ gridTemplateColumns: `repeat(${columns.length}, minmax(120px, 1fr))` }}>
                {row.map((cell, colIndex) => (
                  <div
                    key={colIndex}
                    className={cn(
                      'relative border rounded-md p-3 bg-background hover:bg-accent/10 text-sm text-center cursor-pointer transition-all duration-200 min-h-[40px] flex items-center justify-center',
                      draggedOver?.row === rowIndex && draggedOver?.col === colIndex && 'ring-2 ring-primary bg-primary/10',
                      cell && 'bg-green-50 border-green-200',
                      editingCell?.row === rowIndex && editingCell?.col === colIndex && 'ring-2 ring-blue-500'
                    )}
                    onDrop={(e) => handleDrop(e, rowIndex, colIndex)}
                    onDragOver={(e) => handleDragOver(e, rowIndex, colIndex)}
                    onDragLeave={handleDragLeave}
                    onClick={() => handleCellClick(rowIndex, colIndex)}
                    role="gridcell"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleCellClick(rowIndex, colIndex);
                      }
                    }}
                    aria-label={`Cell ${rowIndex + 1}, ${colIndex + 1}: ${cell || 'empty'}`}
                  >
                    {editingCell?.row === rowIndex && editingCell?.col === colIndex ? (
                      <Input
                        ref={inputRef}
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        onBlur={handleCellEdit}
                        className="h-8 text-xs text-center"
                        placeholder="Enter value"
                      />
                    ) : (
                      <div className="flex items-center gap-2 w-full">
                        {cell ? (
                          <span className="truncate flex-1">
                            {typeof cell === 'string' ? cell : JSON.stringify(cell, null, 2)}
                          </span>
                        ) : (
                          <span className="text-muted-foreground text-xs">Drop value here</span>
                        )}
                        {cell && <GripVertical className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100" />}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              
              {/* Row delete button */}
              <div className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => removeRow(rowIndex)}
                  className="h-8 w-8 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                  aria-label={`Remove row ${rowIndex + 1}`}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {matrix.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          <div className="text-sm">No rows in matrix</div>
          <div className="text-xs mt-1">Click "Add Row" to get started</div>
        </div>
      )}
    </div>
  );
};

export default MatrixBuilder;
