"use client"

import React from "react"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { ChevronDownIcon } from "lucide-react"

interface FieldProps {
  input: any
  value: any
  onChange: (name: string, value: any) => void
}

export function Field({ input, value, onChange }: FieldProps) {
  const [open, setOpen] = React.useState(false)

  const handleChange = (val: any) => {
    if (input.type === "number") val = Number(val)
    if (input.type === "checkbox") val = !!val
    onChange(input.name, val)
  }

  switch (input.type) {
    case "number":
    case "text":
    case "string":
      return (
        <div className="flex flex-col">
          <Input
            type={input.type === "string" ? "text" : input.type}
            id={input.name}
            value={value ?? ""}
            placeholder={input.placeholder}
            required={!!input.required}
            onChange={(e) => handleChange(e.target.value)}
          />
        </div>
      )

    case "textarea":
      return (
        <div className="flex flex-col">
          {input.label && <Label htmlFor={input.name}>{input.label}</Label>}
          <Textarea
            id={input.name}
            value={value}
            required={!!input.required}
            onChange={(e) => handleChange(e.target.value)}
            rows={3}
          />
        </div>
      )

    case "select":
      // Ensure value is a string that matches one of the options
      const normalizedValue = value != null && value !== "" ? String(value) : "";
      const selectValue = normalizedValue || undefined;
      
      return (
        <div className="flex flex-col">
          <Select 
            key={`${input.name}-${selectValue || 'empty'}`}
            value={selectValue} 
            onValueChange={(val) => handleChange(val)}
          >
            <SelectTrigger id={input.name}>
              <SelectValue placeholder={input.placeholder || "Select an option"} />
            </SelectTrigger>
            <SelectContent>
              {input.options?.map((option: any, idx: number) => (
                <SelectItem key={idx} value={String(option.value ?? option)}>
                  {option.label ?? option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )

    case "checkbox":
      return (
        <div className="flex items-center space-x-2">
          <Checkbox
            id={input.name}
            checked={!!value}
            onCheckedChange={(checked) => handleChange(checked)}
          />
          {input.label && <Label htmlFor={input.name}>{input.label}</Label>}
        </div>
      )

    case "calendar":
      return (
        <div className="flex flex-col gap-2">
          <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                id={input.name}
                className="w-36 justify-between font-normal"
              >
                {value ? new Date(value).toLocaleDateString() : "Select date"}
                <ChevronDownIcon />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto overflow-hidden p-0" align="start">
              <Calendar
                mode="single"
                selected={value ? new Date(value) : undefined}
                captionLayout="dropdown"
                onSelect={(date) => {
                  handleChange(date)
                  setOpen(false)
                }}
              />
            </PopoverContent>
          </Popover>
        </div>
      )

    case "json":
      return (
        <div className="flex flex-col">
          <Textarea
            id={input.name}
            value={typeof value === "string" ? value : JSON.stringify(value, null, 2)}
            required={!!input.required}
            onChange={(e) => handleChange(e.target.value)}
            rows={6}
            placeholder={input.placeholder}
            className="font-mono text-sm"
          />
        </div>
      )

    default:
      return (
        <div className="flex flex-col">
          <Input
            type="text"
            id={input.name}
            value={value}
            required={!!input.required}
            onChange={(e) => handleChange(e.target.value)}
          />
        </div>
      )
  }
}
