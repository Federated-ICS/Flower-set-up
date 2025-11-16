"use client"
import type { ReactNode } from "react"

interface ActionButtonProps {
  icon: ReactNode
  label: string
  onClick: () => void
  colorClass: string
}

export function ActionButton({ icon, label, onClick, colorClass }: ActionButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg ${colorClass} hover:bg-opacity-20 transition-all duration-200 text-left font-medium`}
    >
      <span className="text-lg">{icon}</span>
      {label}
    </button>
  )
}
