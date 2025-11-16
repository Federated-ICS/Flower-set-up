"use client"

import { Card } from "./card"
import { ActionButton } from "./action-button"
import { RefreshCw, CheckCircle, Activity } from "lucide-react"

interface QuickActionsCardProps {
  onAction: (action: string) => void
}

export function QuickActionsCard({ onAction }: QuickActionsCardProps) {
  return (
    <Card>
      <h2 className="text-xl font-semibold mb-6 text-white">Quick Actions</h2>

      <div className="space-y-3">
        <ActionButton
          icon={<RefreshCw size={20} />}
          label="Trigger FL Round"
          onClick={() => onAction("trigger-fl")}
          colorClass="bg-blue-500/10 text-blue-400"
        />
        <ActionButton
          icon={<CheckCircle size={20} />}
          label="Acknowledge Alerts"
          onClick={() => onAction("acknowledge-alerts")}
          colorClass="bg-green-500/10 text-green-400"
        />
        <ActionButton
          icon={<Activity size={20} />}
          label="Run Diagnostics"
          onClick={() => onAction("run-diagnostics")}
          colorClass="bg-yellow-500/10 text-yellow-400"
        />
      </div>
    </Card>
  )
}
