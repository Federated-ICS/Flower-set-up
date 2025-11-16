"use client"

import Link from "next/link"
import { AlertTriangle, ChevronLeft, Plus } from "lucide-react"
import { SearchInput } from "./search-input"

interface AlertsHeaderProps {
  searchValue: string
  onSearchChange: (value: string) => void
  onNewAlert: () => void
}

export function AlertsHeader({ searchValue, onSearchChange, onNewAlert }: AlertsHeaderProps) {
  return (
    <div className="mb-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <AlertTriangle size={32} className="text-blue-500" />
          <h1 className="text-4xl font-bold text-white">Alert Dashboard</h1>
        </div>

        <Link href="/" className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors text-sm">
          <ChevronLeft size={16} />
          Back to Dashboard
        </Link>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <SearchInput value={searchValue} onChange={onSearchChange} />
        </div>
        <button
          onClick={onNewAlert}
          className="flex items-center justify-center md:justify-start gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors font-medium"
        >
          <Plus size={16} />
          New Alert
        </button>
      </div>
    </div>
  )
}
