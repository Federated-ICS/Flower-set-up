"use client"

import { Card } from "./card"
import { ProgressBar } from "./progress-bar"

interface ClientCardProps {
  name: string
  status: "active" | "delayed" | "offline"
  progress: number
  loss?: number | null
  accuracy?: number | null
}

export const ClientCard = ({ name, status, progress, loss, accuracy }: ClientCardProps) => {
  const statusColors: Record<string, string> = {
    active: "bg-green-500",
    delayed: "bg-yellow-500",
    offline: "bg-red-500",
  }

  const barColor: Record<string, string> = {
    active: "bg-green-500",
    delayed: "bg-yellow-500",
    offline: "bg-red-500",
  }

  return (
    <Card className="hover:border-blue-500 hover:-translate-y-0.5 transition-all">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-white">{name}</h3>
        <div className={`w-3 h-3 rounded-full ${statusColors[status]}`} aria-label={`Status: ${status}`} />
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-400">Training Progress</span>
            <span className="text-sm font-mono text-blue-400">{progress}%</span>
          </div>
          <ProgressBar percentage={progress} />
        </div>

        <div className="flex justify-between items-end pt-2 border-t border-slate-700">
          <div>
            <p className="text-xs text-gray-500">Loss</p>
            <p className="text-sm font-mono text-gray-400">
              {loss != null ? loss.toFixed(2) : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Accuracy</p>
            <p className="text-sm font-mono text-gray-400">
              {accuracy != null ? `${accuracy.toFixed(1)}%` : 'N/A'}
            </p>
          </div>
        </div>
      </div>
    </Card>
  )
}
