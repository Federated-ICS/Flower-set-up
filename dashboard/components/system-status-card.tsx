import { Card } from "./card"
import { StatusIndicator } from "./status-indicator"

interface SystemStatusCardProps {
  activeAlerts: number
  flProgress: number
  predictionAccuracy: number
}

export function SystemStatusCard({ activeAlerts, flProgress, predictionAccuracy }: SystemStatusCardProps) {
  return (
    <Card glowEffect>
      <h2 className="text-xl font-semibold mb-6 text-white">System Status</h2>

      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <StatusIndicator status="operational" />
          <span className="text-gray-300">System operational</span>
        </div>

        <div className="pt-4 border-t border-slate-700">
          <div className="text-sm text-gray-400 mb-1">Active Alerts</div>
          <div className="text-2xl font-mono font-semibold text-red-400">{activeAlerts}</div>
        </div>

        <div className="pt-4 border-t border-slate-700">
          <div className="text-sm text-gray-400 mb-1">FL Progress</div>
          <div className="text-2xl font-mono font-semibold text-blue-400">{flProgress}%</div>
        </div>

        <div className="pt-4 border-t border-slate-700">
          <div className="text-sm text-gray-400 mb-1">Prediction Accuracy</div>
          <div className="text-2xl font-mono font-semibold text-green-400">{predictionAccuracy}%</div>
        </div>
      </div>
    </Card>
  )
}
