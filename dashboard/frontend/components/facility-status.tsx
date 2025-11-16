import { StatusIndicator } from "./status-indicator"

interface FacilityStatusProps {
  name: string
  status: "active" | "delayed"
}

export function FacilityStatus({ name, status }: FacilityStatusProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <StatusIndicator status={status === "active" ? "operational" : "warning"} />
      <span className="text-xs text-gray-400 text-center">{name}</span>
    </div>
  )
}
