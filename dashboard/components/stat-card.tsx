"use client"

import { Card } from "./card"
import { ProgressBar } from "./progress-bar"

interface StatCardProps {
  label: string
  value: number
  color: "red" | "yellow" | "green" | "blue"
  percentage: number
}

export function StatCard({ label, value, color, percentage }: StatCardProps) {
  const textColors = {
    red: "text-red-400",
    yellow: "text-yellow-400",
    green: "text-green-400",
    blue: "text-blue-400",
  }

  const progressColors = {
    red: "bg-red-500",
    yellow: "bg-yellow-500",
    green: "bg-green-500",
    blue: "bg-blue-500",
  }

  return (
    <Card className="p-4 rounded-lg">
      <div className="flex justify-between items-start mb-3">
        <span className="text-gray-400 text-sm">{label}</span>
        <span className={`text-xl font-medium ${textColors[color]}`}>{value}</span>
      </div>
      <ProgressBar percentage={percentage} />
    </Card>
  )
}
