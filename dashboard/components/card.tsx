import type { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface CardProps {
  children: ReactNode
  className?: string
  glowEffect?: boolean
}

export function Card({ children, className, glowEffect = false }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl p-6 border border-slate-700 bg-slate-900/70 transition-all duration-300 ease-in-out hover:border-blue-500 hover:-translate-y-0.5",
        glowEffect && "shadow-lg shadow-blue-500/50",
        className,
      )}
    >
      {children}
    </div>
  )
}
