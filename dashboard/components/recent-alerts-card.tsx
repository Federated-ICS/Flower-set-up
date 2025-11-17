import { Card } from "./card"
import { StatusIndicator } from "./status-indicator"
import Link from "next/link"

interface Alert {
  id: string
  title: string
  severity: "critical" | "high" | "low"
  facility: string
  timestamp: string
}

interface RecentAlertsCardProps {
  alerts: Alert[]
}

export function RecentAlertsCard({ alerts }: RecentAlertsCardProps) {
  const getSeverityStatus = (severity: string) => {
    switch (severity) {
      case "critical":
        return "critical"
      case "high":
        return "warning"
      default:
        return "operational"
    }
  }

  return (
    <Card>
      <h2 className="text-xl font-semibold mb-6 text-white">Recent Alerts</h2>

      {alerts.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-400">No recent alerts</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.slice(0, 3).map((alert) => (
            <div
              key={alert.id}
              className="flex items-start gap-3 pb-4 border-b border-slate-700 last:border-b-0 last:pb-0"
            >
              <StatusIndicator status={getSeverityStatus(alert.severity)} />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-white">{alert.title}</p>
                <p className="text-sm text-gray-400">
                  {alert.facility} • {alert.timestamp}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-slate-700">
        <Link href="/alerts" className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
          View All Alerts →
        </Link>
      </div>
    </Card>
  )
}
