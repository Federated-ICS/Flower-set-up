import { Card } from "./card"
import { ProgressBar } from "./progress-bar"
import Link from "next/link"

interface AttackPredictionCardProps {
  techniqueId: string
  techniqueName: string
  confidence: number
  timelineProgress: number
}

export function AttackPredictionCard({
  techniqueId,
  techniqueName,
  confidence,
  timelineProgress,
}: AttackPredictionCardProps) {
  return (
    <Card className="md:col-span-2">
      <h2 className="text-xl font-semibold mb-6 text-white">Attack Prediction</h2>

      <div className="space-y-6">
        <div>
          <p className="text-sm text-gray-400">Predicted Technique</p>
          <p className="font-mono text-white">
            {techniqueId} • {techniqueName}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-400 mb-2">Confidence</p>
          <p className="text-lg font-semibold text-green-400">{confidence}%</p>
        </div>

        <div>
          <p className="text-sm text-gray-400 mb-3">Threat Level</p>
          <ProgressBar percentage={timelineProgress} showGradient />
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>Low</span>
            <span>Medium</span>
            <span>Critical</span>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-700">
          <Link
            href="/attack-graph"
            className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
          >
            View Attack Graph →
          </Link>
        </div>
      </div>
    </Card>
  )
}
