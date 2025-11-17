"use client"

import { Card } from "./card"
import { ProgressBar } from "./progress-bar"
import { CircularProgress } from "./circular-progress"
import { formatTimeRemaining } from "@/utils/format-time"

interface RoundProgressCardProps {
  roundNumber: number
  progress: number
  phase: string
  timeRemaining: number
  clientsActive: number
  totalClients: number
  epsilon: number
  modelAccuracy: number | null
}

export function RoundProgressCard({
  roundNumber,
  progress,
  phase,
  timeRemaining,
  clientsActive,
  totalClients,
  epsilon,
  modelAccuracy,
}: RoundProgressCardProps) {
  const phaseLabels: Record<string, string> = {
    distributing: "Distributing Global Model",
    training: "Training on Local Data",
    aggregating: "Aggregating Model Updates",
    complete: "Round Complete",
  }

  return (
    <Card glowEffect className="lg:col-span-2">
      <h2 className="text-2xl font-semibold text-white mb-6">Current Round Progress</h2>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Circular Progress */}
        <div className="flex-1">
          <CircularProgress progress={progress} />
          <p className="text-center mt-4 font-mono text-gray-400">Round #{roundNumber}</p>
        </div>

        {/* Details */}
        <div className="flex-1 space-y-6">
          {/* Phase */}
          <div>
            <p className="text-sm text-gray-400 mb-2">Current Phase</p>
            <p className="text-lg font-medium text-white">{phaseLabels[phase] || phase}</p>
            <ProgressBar percentage={progress} className="mt-3" />
          </div>

          {/* Time Remaining */}
          <div>
            <p className="text-sm text-gray-400">Estimated Time</p>
            <p className="text-lg font-mono text-blue-400">{formatTimeRemaining(timeRemaining)}</p>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-700">
            <div>
              <p className="text-xs text-gray-500">Clients Active</p>
              <p className="text-lg font-mono text-green-400">
                {clientsActive}/{totalClients}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Privacy (ε)</p>
              <p className="text-lg font-mono text-yellow-400">{epsilon?.toFixed(2) ?? '0.00'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Model Accuracy</p>
              <p className="text-lg font-mono text-green-400">{modelAccuracy?.toFixed(1) ?? '0.0'}%</p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
