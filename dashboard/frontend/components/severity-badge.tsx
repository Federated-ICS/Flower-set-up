interface SeverityBadgeProps {
  severity: "critical" | "high" | "medium" | "low"
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const colors = {
    critical: "bg-red-900/50 text-red-400",
    high: "bg-yellow-900/50 text-yellow-400",
    medium: "bg-blue-900/50 text-blue-400",
    low: "bg-green-900/50 text-green-400",
  }

  return (
    <span className={`px-2 py-1 text-xs rounded-full font-medium ${colors[severity]}`}>
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
    </span>
  )
}
