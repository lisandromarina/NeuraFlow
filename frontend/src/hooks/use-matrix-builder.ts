import { useState, useCallback, useEffect, useMemo } from 'react';

export interface MatrixInitialData {
  matrix?: (string | object)[][];
  columns?: string[];
}

export interface MatrixStats {
  filledCells: number;
  totalCells: number;
  rows: number;
  columns: number;
}

export interface MatrixExportData {
  columns: string[];
  values: (string | object)[][];
  metadata: {
    rows: number;
    columns: number;
    lastUpdated: string;
  };
}

export const useMatrixBuilder = (initialRows = 2, initialColumns = 2, initialData?: MatrixInitialData) => {
  const [matrix, setMatrix] = useState<(string | object)[][]>(
    initialData?.matrix || Array.from({ length: initialRows }, () => Array.from({ length: initialColumns }, () => ''))
  );
  const [columns, setColumns] = useState<string[]>(
    initialData?.columns || Array.from({ length: initialColumns }, (_, i) => `Column ${i + 1}`)
  );

  // Update matrix and columns when initialData changes
  useEffect(() => {
    if (initialData?.matrix) {
      setMatrix(initialData.matrix);
    }
    if (initialData?.columns) {
      setColumns(initialData.columns);
    }
  }, [initialData]);

  const addRow = useCallback(() => {
    setMatrix((prev) => [...prev, Array(columns.length).fill('')]);
  }, [columns.length]);

  const removeRow = useCallback((rowIndex: number) => {
    setMatrix((prev) => prev.filter((_, i) => i !== rowIndex));
  }, []);

  const addColumn = useCallback(() => {
    setColumns((prev) => [...prev, `Column ${prev.length + 1}`]);
    setMatrix((prev) => prev.map((row) => [...row, '']));
  }, []);

  const removeColumn = useCallback((colIndex: number) => {
    setColumns((prev) => prev.filter((_, i) => i !== colIndex));
    setMatrix((prev) => prev.map((row) => row.filter((_, i) => i !== colIndex)));
  }, []);

  const updateCell = useCallback((rowIndex: number, colIndex: number, value: string | object) => {
    setMatrix((prev) => {
      const newMatrix = prev.map((r) => [...r]);
      newMatrix[rowIndex][colIndex] = value;
      return newMatrix;
    });
  }, []);

  const updateColumn = useCallback((colIndex: number, newName: string) => {
    setColumns((prev) => {
      const newColumns = [...prev];
      newColumns[colIndex] = newName;
      return newColumns;
    });
  }, []);

  const handleDropCell = useCallback((rowIndex: number, colIndex: number, value: string | object) => {
    updateCell(rowIndex, colIndex, value);
  }, [updateCell]);

  const clearMatrix = useCallback(() => {
    setMatrix((prev) => prev.map(row => row.map(() => '')));
  }, []);

  // Calculate matrix statistics
  const stats = useMemo((): MatrixStats => {
    const filledCells = matrix.flat().filter(cell => {
      if (typeof cell === 'string') return cell.trim() !== '';
      if (typeof cell === 'object' && cell !== null) return Object.keys(cell).length > 0;
      return false;
    }).length;
    
    const totalCells = matrix.length * columns.length;
    
    return {
      filledCells,
      totalCells,
      rows: matrix.length,
      columns: columns.length
    };
  }, [matrix, columns]);

  // Export matrix data in the format expected by LinkDialogContainer
  const exportMatrix = useCallback((): MatrixExportData => {
    return {
      columns,
      values: matrix,
      metadata: {
        rows: matrix.length,
        columns: columns.length,
        lastUpdated: new Date().toISOString()
      }
    };
  }, [matrix, columns]);

  // Import matrix data
  const importMatrix = useCallback((data: { columns: string[], data: (string | object)[][] }) => {
    setColumns(data.columns);
    setMatrix(data.data);
  }, []);

  // Process initial data from configuration (moved from LinkDialogContainer)
  const processInitialData = useCallback((linkableField: any, currentConfig: Record<string, any>) => {
    if (linkableField && currentConfig[linkableField.field_name]) {
      const configValue = currentConfig[linkableField.field_name];
      if (Array.isArray(configValue)) {
        return {
          matrix: configValue,
          columns: Array.from({ length: configValue[0]?.length || 2 }, (_, i) => `Column ${i + 1}`)
        };
      }
    }
    return undefined;
  }, []);

  // Reset matrix to initial state
  const resetMatrix = useCallback(() => {
    setMatrix(Array.from({ length: initialRows }, () => Array.from({ length: initialColumns }, () => '')));
    setColumns(Array.from({ length: initialColumns }, (_, i) => `Column ${i + 1}`));
  }, [initialRows, initialColumns]);

  // Validate matrix data
  const validateMatrix = useCallback(() => {
    const errors: string[] = [];
    
    if (matrix.length === 0) {
      errors.push('Matrix must have at least one row');
    }
    
    if (columns.length === 0) {
      errors.push('Matrix must have at least one column');
    }
    
    // Check for inconsistent row lengths
    const rowLengths = matrix.map(row => row.length);
    const uniqueLengths = new Set(rowLengths);
    if (uniqueLengths.size > 1) {
      errors.push('All rows must have the same number of columns');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }, [matrix, columns]);

  return {
    // Core matrix data
    matrix,
    columns,
    
    // Matrix manipulation functions
    addRow,
    removeRow,
    addColumn,
    removeColumn,
    updateCell,
    updateColumn,
    handleDropCell,
    clearMatrix,
    resetMatrix,
    
    // Data processing functions
    exportMatrix,
    importMatrix,
    processInitialData,
    validateMatrix,
    
    // Statistics and metadata
    stats,
    
    // Direct setters (for advanced use cases)
    setMatrix,
    setColumns,
  };
};
