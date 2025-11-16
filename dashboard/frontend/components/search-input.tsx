"use client"

import { Search } from "lucide-react"

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
}

export function SearchInput({ value, onChange }: SearchInputProps) {
  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 text-sm" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search alerts..."
        aria-label="Search alerts by keyword"
        className="w-full bg-gray-800 border border-gray-700 rounded-md px-4 py-2 pl-10 text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
    </div>
  )
}
