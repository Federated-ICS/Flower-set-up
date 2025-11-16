interface ProgressBarProps {
  percentage: number
  className?: string
  showGradient?: boolean
}

export function ProgressBar({ percentage, className, showGradient = false }: ProgressBarProps) {
  return (
    <div className={cn("w-full h-2 bg-slate-700 rounded-full overflow-hidden", className)}>
      <div
        className={cn(
          "h-full transition-all duration-300 ease-out",
          showGradient ? "bg-gradient-to-r from-yellow-500 to-red-500" : "bg-blue-500",
        )}
        style={{ width: `${Math.min(percentage, 100)}%` }}
      />
    </div>
  )
}

function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(" ")
}
