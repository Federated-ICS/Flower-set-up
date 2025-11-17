"use client"

interface RoundStatusBadgeProps {
  status: "in-progress" | "completed" | "failed"
}

export function RoundStatusBadge({ status }: RoundStatusBadgeProps) {
  const statusConfig = {
    "in-progress": { bg: "bg-blue-900/50", text: "text-blue-400" },
    completed: { bg: "bg-green-900/50", text: "text-green-400" },
    failed: { bg: "bg-red-900/50", text: "text-red-400" },
  }

  const { bg, text } = statusConfig[status]
  const label = status === "in-progress" ? "In Progress" : status.charAt(0).toUpperCase() + status.slice(1)

  return (
    <span className={`px-2 py-1 text-xs rounded-full ${bg} ${text}`} aria-label={`Status: ${label}`}>
      {label}
    </span>
  )
}
