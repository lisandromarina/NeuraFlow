import { useState, useCallback, useMemo } from 'react';
import { useMatrixBuilder, type MatrixInitialData, type MatrixStats } from './use-matrix-builder';

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'email' | 'select' | 'textarea';
  required?: boolean;
  options?: string[];
  placeholder?: string;
}

export interface FormData {
  [key: string]: any;
}

export interface FormStats {
  filledFields: number;
  totalFields: number;
  isValid: boolean;
  errors: string[];
}

// Example of how the matrix builder logic can be reused for forms
export const useFormBuilder = (fields: FormField[], initialData?: FormData) => {
  const [formData, setFormData] = useState<FormData>(initialData || {});
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Calculate form statistics (similar to matrix stats)
  const stats = useMemo((): FormStats => {
    const filledFields = fields.filter(field => {
      const value = formData[field.name];
      return value !== undefined && value !== null && value !== '';
    }).length;

    const validationErrors: string[] = [];
    fields.forEach(field => {
      const value = formData[field.name];
      if (field.required && (!value || value === '')) {
        validationErrors.push(`${field.label} is required`);
      }
    });

    return {
      filledFields,
      totalFields: fields.length,
      isValid: validationErrors.length === 0,
      errors: validationErrors
    };
  }, [formData, fields]);

  const updateField = useCallback((fieldName: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
    
    // Clear error when field is updated
    if (errors[fieldName]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    }
  }, [errors]);

  const validateForm = useCallback(() => {
    const newErrors: Record<string, string> = {};
    
    fields.forEach(field => {
      const value = formData[field.name];
      if (field.required && (!value || value === '')) {
        newErrors[field.name] = `${field.label} is required`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData, fields]);

  const resetForm = useCallback(() => {
    setFormData({});
    setErrors({});
  }, []);

  const exportFormData = useCallback(() => {
    return {
      data: formData,
      metadata: {
        fields: fields.length,
        filledFields: stats.filledFields,
        lastUpdated: new Date().toISOString()
      }
    };
  }, [formData, fields.length, stats.filledFields]);

  return {
    formData,
    errors,
    stats,
    updateField,
    validateForm,
    resetForm,
    exportFormData,
    setFormData,
  };
};

// Example of how you could use both matrix and form builders together
export const useHybridBuilder = (type: 'matrix' | 'form', config: any) => {
  // This demonstrates how the same pattern can be used for different input types
  if (type === 'matrix') {
    return useMatrixBuilder(config.initialRows, config.initialColumns, config.initialData);
  } else {
    return useFormBuilder(config.fields, config.initialData);
  }
};
