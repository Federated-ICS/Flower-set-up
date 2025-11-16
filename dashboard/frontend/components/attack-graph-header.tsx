"use client"

import Link from "next/link"
import { Activity, ChevronLeft, Maximize2, Sidebar } from "lucide-react"

interface AttackGraphHeaderProps {
  onResetView: () => void
  onToggleSidebar: () => void
}

export function AttackGraphHeader({ onResetView, onToggleSidebar }: AttackGraphHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8">
      <div className="flex items-center gap-3">
        <Activity size={32} className="text-blue-400" />
        <h1 className="text-4xl font-bold gradient-text">Attack Graph</h1>
      </div>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/"
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-gray-400 hover:text-blue-400 transition-colors"
        >
          <ChevronLeft size={18} />
          Back to Dashboard
        </Link>

        <button
          onClick={onResetView}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-gray-400 hover:text-blue-400 transition-colors"
          aria-label="Reset view"
        >
          <Maximize2 size={18} />
          Reset View
        </button>

        <button
          onClick={onToggleSidebar}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-gray-400 hover:text-blue-400 transition-colors"
          aria-label="Toggle details panel"
        >
          <Sidebar size={18} />
          Details Panel
        </button>
      </div>
    </div>
  )
}
