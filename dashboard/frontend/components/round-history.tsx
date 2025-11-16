"use client"

import Link from "next/link"
import { ChevronRight } from "lucide-react"
import { Card } from "./card"
import { RoundHistoryRow } from "./round-history-row"

interface RoundHistoryItem {
  roundNumber: number
  status: "in-progress" | "completed" | "failed"
  duration: number
  clients: string
  accuracyChange: number | null
  epsilon: number
}

interface RoundHistoryProps {
  rounds: RoundHistoryItem[]
}

export function RoundHistory({ rounds }: RoundHistoryProps) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-white">Round History</h2>
        <Link
          href="/fl-status/history"
          className="flex items-center gap-1 text-blue-400 hover:text-blue-300 transition-colors text-sm"
        >
          View Full History
          <ChevronRight size={16} />
        </Link>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-slate-800 border-b border-slate-700">
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Round
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Duration
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Clients
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Accuracy
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Privacy (ε)
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {rounds.map((round) => (
              <RoundHistoryRow
                key={round.roundNumber}
                roundNumber={round.roundNumber}
                status={round.status}
                duration={round.duration}
                clients={round.clients}
                accuracyChange={round.accuracyChange}
                epsilon={round.epsilon}
              />
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
