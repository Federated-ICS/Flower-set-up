"use client"

import { Card } from "./card"
import { AlertTableRow } from "./alert-table-row"
import type { Alert } from "@/lib/api-client"

interface AlertTableProps {
  alerts: Alert[]
  onActionClick: (alertId: string, action: string) => void
}

export function AlertTable({ alerts, onActionClick }: AlertTableProps) {
  return (
    <Card className="overflow-x-auto p-0">
      <table className="w-full">
        <thead className="bg-gray-800">
          <tr>
            <th
              scope="col"
              className="px-6 py-4 text-left uppercase tracking-wider text-xs font-semibold text-gray-400"
            >
              Severity
            </th>
            <th
              scope="col"
              className="px-6 py-4 text-left uppercase tracking-wider text-xs font-semibold text-gray-400"
            >
              Alert
            </th>
            <th
              scope="col"
              className="px-6 py-4 text-left uppercase tracking-wider text-xs font-semibold text-gray-400"
            >
              Facility
            </th>
            <th
              scope="col"
              className="px-6 py-4 text-left uppercase tracking-wider text-xs font-semibold text-gray-400"
            >
              Source
            </th>
            <th
              scope="col"
              className="px-6 py-4 text-left uppercase tracking-wider text-xs font-semibold text-gray-400"
            >
              Time
            </th>
            <th
              scope="col"
              className="px-6 py-4 text-left uppercase tracking-wider text-xs font-semibold text-gray-400"
            >
              Status
            </th>
            <th
              scope="col"
              className="px-6 py-4 text-left uppercase tracking-wider text-xs font-semibold text-gray-400"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {alerts.map((alert) => (
            <AlertTableRow key={alert.id} alert={alert} onActionClick={onActionClick} />
          ))}
        </tbody>
      </table>
    </Card>
  )
}
