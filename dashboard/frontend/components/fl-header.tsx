"use client"

import Link from "next/link"
import { Cpu, ChevronLeft, RefreshCw, Settings } from "lucide-react"

interface FLHeaderProps {
  onTriggerRound: () => void
  onConfiguration: () => void
}

export function FLHeader({ onTriggerRound, onConfiguration }: FLHeaderProps) {
  return (
    <div className="mb-8">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Cpu size={32} className="text-blue-400" />
          <div>
            <h1 className="text-4xl font-bold text-white">Federated Learning Status</h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <ChevronLeft size={20} />
            <span className="text-sm">Back</span>
          </Link>

          <button
            onClick={onTriggerRound}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            <RefreshCw size={20} />
            <span className="text-sm">Trigger Round</span>
          </button>

          <button
            onClick={onConfiguration}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
          >
            <Settings size={20} />
            <span className="text-sm">Config</span>
          </button>
        </div>
      </div>
    </div>
  )
}
