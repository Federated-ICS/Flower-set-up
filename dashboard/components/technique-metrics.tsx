"use client"

interface TechniqueMetricsProps {
  type: "current" | "predicted"
  probability: number
  platforms: string[]
  tactics: string[]
}

export function TechniqueMetrics({ type, probability, platforms, tactics }: TechniqueMetricsProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <p className="text-gray-400 text-sm mb-1">Status</p>
        <div
          className={cn(
            "inline-block px-3 py-1 rounded-full text-sm font-medium",
            type === "current" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400",
          )}
        >
          {type === "current" ? "Current Attack" : "Predicted Attack"}
        </div>
      </div>

      <div>
        <p className="text-gray-400 text-sm mb-1">Confidence</p>
        <p className="text-lg font-medium text-blue-400">{Math.round(probability * 100)}%</p>
      </div>

      <div>
        <p className="text-gray-400 text-sm mb-1">Platforms</p>
        <p className="text-sm text-gray-300">{platforms.join(", ")}</p>
      </div>

      <div>
        <p className="text-gray-400 text-sm mb-1">Tactics</p>
        <p className="text-sm text-gray-300">{tactics.join(", ")}</p>
      </div>
    </div>
  )
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ")
}
