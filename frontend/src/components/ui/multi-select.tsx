import * as React from "react"
import { X } from "lucide-react"

interface Option {
  label: string
  value: string
}

interface MultiSelectProps {
  options: Option[]
  value: string[]
  onChange: (value: string[]) => void
  placeholder?: string
  className?: string
  id?: string
}

export function MultiSelect({
  options,
  value,
  onChange,
  placeholder = "Select options...",
  className,
  id,
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = React.useState(false)

  const handleSelect = (optionValue: string) => {
    onChange(
      value.includes(optionValue)
        ? value.filter((v) => v !== optionValue)
        : [...value, optionValue]
    )
  }

  const handleUnselect = (optionValue: string) => {
    onChange(value.filter((v) => v !== optionValue))
  }

  return (
    <div className={`relative ${className}`}>
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="min-h-[40px] w-full border rounded-md p-2 cursor-pointer flex flex-wrap gap-1"
      >
        {value.map((optionValue) => (
          <span
            key={optionValue}
            className="bg-gray-200 px-2 py-1 rounded-full text-sm flex items-center gap-1"
          >
            {options.find((o) => o.value === optionValue)?.label}
            <button
              onClick={(e) => {
                e.stopPropagation()
                handleUnselect(optionValue)
              }}
              className="hover:bg-gray-300 rounded-full p-1"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
        {value.length === 0 && (
          <span className="text-gray-500">{placeholder}</span>
        )}
      </div>
      
      {isOpen && (
        <div className="absolute w-full mt-1 max-h-[200px] overflow-auto border rounded-md bg-white shadow-lg z-50">
          {options.map((option) => (
            <div
              key={option.value}
              onClick={() => handleSelect(option.value)}
              className={`p-2 cursor-pointer hover:bg-gray-100 ${
                value.includes(option.value) ? "bg-gray-50" : ""
              }`}
            >
              {option.label}
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 