"use client"

import { useState } from "react"
import { MoreVertical, Check, X, AlertTriangle } from "lucide-react"
import { SeverityBadge } from "./severity-badge"
import { StatusBadge } from "./status-badge"
import { SourceIndicator } from "./source-indicator"
import type { Alert } from "@/lib/api-client"

interface AlertTableRowProps {
  alert: Alert
  onActionClick: (alertId: string, action: string) => void
}

export const AlertTableRow = ({ alert, onActionClick }: AlertTableRowProps) => {
  const [showActions, setShowActions] = useState(false)

  // Format timestamp to relative time
  const getRelativeTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins} min ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  }

  // Get primary source for display
  const primarySource = alert.sources?.[0]?.model_name || "System"

  return (
    <tr className="hover:bg-gray-800/50 transition-colors">
      <td className="px-6 py-4">
        <SeverityBadge severity={alert.severity} />
      </td>
      <td className="px-6 py-4">
        <div>
          <p className="font-medium text-white">{alert.title}</p>
          <p className="text-sm text-gray-400">{alert.description}</p>
        </div>
      </td>
      <td className="px-6 py-4 text-gray-400">{alert.facility_id}</td>
      <td className="px-6 py-4">
        <SourceIndicator source={primarySource} severity={alert.severity} />
      </td>
      <td className="px-6 py-4 text-gray-400 text-sm">{getRelativeTime(alert.timestamp)}</td>
      <td className="px-6 py-4">
        <StatusBadge status={alert.status} />
      </td>
      <td className="px-6 py-4 relative">
        <button
          onClick={() => setShowActions(!showActions)}
          className="text-gray-400 hover:text-white transition-colors"
          aria-label={`Actions for alert ${alert.id}`}
        >
          <MoreVertical size={16} />
        </button>
        
        {showActions && (
          <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-md shadow-lg z-10">
            <button
              onClick={() => {
                onActionClick(alert.id, "acknowledged")
                setShowActions(false)
              }}
              className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
            >
              <Check size={14} />
              Acknowledge
            </button>
            <button
              onClick={() => {
                onActionClick(alert.id, "resolved")
                setShowActions(false)
              }}
              className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
            >
              <Check size={14} />
              Resolve
            </button>
            <button
              onClick={() => {
                onActionClick(alert.id, "false-positive")
                setShowActions(false)
              }}
              className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
            >
              <X size={14} />
              Mark as False Positive
            </button>
          </div>
        )}
      </td>
    </tr>
  )
}
