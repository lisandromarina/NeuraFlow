import React from "react";

interface FieldProps {
  input: any;
  value: any;
  onChange: (name: string, value: any) => void;
}

export function Field({ input, value, onChange }: FieldProps) {
  const commonProps = {
    id: input.name || input.key,
    required: !!input.required,
    className: "w-full border p-1 rounded",
  };

  const handleChange = (e: React.ChangeEvent<any>) => {
    let newValue: any = e.target.value;

    if (input.type === "number") {
      newValue = Number(newValue);
    }
    if (input.type === "checkbox") {
      newValue = e.target.checked;
    }

    onChange(input.name, newValue);
  };

  switch (input.type) {
    case "number":
      return (
        <input
          type="number"
          {...commonProps}
          value={value}
          onChange={handleChange}
        />
      );
    case "textarea":
      return (
        <textarea
          {...commonProps}
          rows={3}
          value={value}
          onChange={handleChange}
        />
      );
    case "select":
      return (
        <select {...commonProps} value={value} onChange={handleChange}>
          {input.options?.map((option: any, idx: number) => (
            <option key={idx} value={option.value ?? option}>
              {option.label ?? option}
            </option>
          ))}
        </select>
      );
    case "checkbox":
      return (
        <input
          type="checkbox"
          id={commonProps.id}
          checked={!!value}
          required={commonProps.required}
          className="mr-2"
          onChange={handleChange}
        />
      );
    default:
      return (
        <input
          type="text"
          {...commonProps}
          value={value}
          onChange={handleChange}
        />
      );
  }
}
