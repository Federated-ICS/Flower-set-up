"use client"

import { RoundStatusBadge } from "./round-status-badge"
import { formatDuration } from "@/utils/format-time"

interface RoundHistoryRowProps {
  roundNumber: number
  status: "in-progress" | "completed" | "failed"
  duration: number
  clients: string
  accuracyChange: number | null
  epsilon: number
}

export function RoundHistoryRow({
  roundNumber,
  status,
  duration,
  clients,
  accuracyChange,
  epsilon,
}: RoundHistoryRowProps) {
  return (
    <tr className="hover:bg-slate-800/50 transition-colors">
      <td className="px-6 py-4 whitespace-nowrap font-medium text-white">#{roundNumber}</td>
      <td className="px-6 py-4 whitespace-nowrap">
        <RoundStatusBadge status={status} />
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-gray-400">{formatDuration(duration)}</td>
      <td className="px-6 py-4 whitespace-nowrap text-gray-400">{clients}</td>
      <td className="px-6 py-4 whitespace-nowrap">
        {accuracyChange !== null ? (
          <span className={accuracyChange >= 0 ? "text-green-400" : "text-red-400"}>
            {accuracyChange >= 0 ? "+" : ""}
            {accuracyChange.toFixed(2)}%
          </span>
        ) : (
          <span className="text-gray-500">-</span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-gray-400">{epsilon.toFixed(2)}</td>
    </tr>
  )
}
