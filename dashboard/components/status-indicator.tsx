interface StatusIndicatorProps {
  status: "operational" | "warning" | "critical"
}

export function StatusIndicator({ status }: StatusIndicatorProps) {
  const statusConfig = {
    operational: {
      color: "bg-green-500",
      glow: "cyber-glow-green",
    },
    warning: {
      color: "bg-yellow-500",
      glow: "cyber-glow-yellow",
    },
    critical: {
      color: "bg-red-500",
      glow: "cyber-glow-red",
    },
  }

  const config = statusConfig[status]

  return <div className={`w-2.5 h-2.5 rounded-full ${config.color} ${config.glow}`} aria-label={`Status: ${status}`} />
}
