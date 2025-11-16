"use client"

import { StatCard } from "./stat-card"

interface AlertStatsProps {
  totalAlerts: number
  critical: number
  unresolved: number
  falsePositives: number
}

export function AlertStats({ totalAlerts, critical, unresolved, falsePositives }: AlertStatsProps) {
  const criticalPercent = totalAlerts > 0 ? (critical / totalAlerts) * 100 : 0
  const unresolvedPercent = totalAlerts > 0 ? (unresolved / totalAlerts) * 100 : 0
  const falsePositivesPercent = totalAlerts > 0 ? (falsePositives / totalAlerts) * 100 : 0

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <StatCard label="Total Alerts" value={totalAlerts} color="blue" percentage={100} />
      <StatCard label="Critical" value={critical} color="red" percentage={criticalPercent} />
      <StatCard label="Unresolved" value={unresolved} color="yellow" percentage={unresolvedPercent} />
      <StatCard label="False Positives" value={falsePositives} color="green" percentage={falsePositivesPercent} />
    </div>
  )
}
