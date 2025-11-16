interface SourceIndicatorProps {
  source: string
  severity: "critical" | "high" | "medium" | "low"
}

export function SourceIndicator({ source, severity }: SourceIndicatorProps) {
  const dotColors = {
    critical: "bg-red-500",
    high: "bg-yellow-500",
    medium: "bg-blue-500",
    low: "bg-green-500",
  }

  return (
    <div className="flex items-center">
      <div className={`w-2 h-2 rounded-full mr-2 ${dotColors[severity]}`} />
      <span className="text-gray-400 text-sm">{source}</span>
    </div>
  )
}
