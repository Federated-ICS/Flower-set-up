"use client"

interface SeverityFilterButtonProps {
  label: string
  severity: string
  isActive: boolean
  onClick: (severity: string) => void
}

const severityColors = {
  critical: "bg-red-900/50 text-red-400 hover:bg-red-900/70",
  high: "bg-yellow-900/50 text-yellow-400 hover:bg-yellow-900/70",
  medium: "bg-blue-900/50 text-blue-400 hover:bg-blue-900/70",
  low: "bg-green-900/50 text-green-400 hover:bg-green-900/70",
  all: "bg-gray-700 text-gray-300 hover:bg-gray-600",
}

export function SeverityFilterButton({ label, severity, isActive, onClick }: SeverityFilterButtonProps) {
  const baseClass = "px-3 py-1 rounded-md text-sm font-medium transition-all hover:opacity-80"
  const activeClass = isActive
    ? "bg-blue-500 text-white"
    : severityColors[severity as keyof typeof severityColors] || severityColors.all

  return (
    <button onClick={() => onClick(severity)} className={`${baseClass} ${activeClass}`} aria-pressed={isActive}>
      {label}
    </button>
  )
}
