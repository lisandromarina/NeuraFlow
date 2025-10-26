import { useState, useCallback } from 'react';

export const useMatrixBuilder = (initialRows = 2, initialColumns = 2, initialData?: { matrix?: (string | object)[][], columns?: string[] }) => {
  const [matrix, setMatrix] = useState<(string | object)[][]>(
    initialData?.matrix || Array.from({ length: initialRows }, () => Array.from({ length: initialColumns }, () => ''))
  );
  const [columns, setColumns] = useState<string[]>(
    initialData?.columns || Array.from({ length: initialColumns }, (_, i) => `Column ${i + 1}`)
  );

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

  const exportMatrix = useCallback(() => {
    return {
      columns,
      data: matrix,
      metadata: {
        rows: matrix.length,
        columns: columns.length,
        lastUpdated: new Date().toISOString()
      }
    };
  }, [matrix, columns]);

  const importMatrix = useCallback((data: { columns: string[], data: string[][] }) => {
    setColumns(data.columns);
    setMatrix(data.data);
  }, []);

  return {
    matrix,
    columns,
    addRow,
    removeRow,
    addColumn,
    removeColumn,
    updateCell,
    updateColumn,
    handleDropCell,
    clearMatrix,
    exportMatrix,
    importMatrix,
    setMatrix,
  };
};
