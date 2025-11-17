interface StatusBadgeProps {
  status: "new" | "acknowledged" | "resolved" | "false-positive"
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const statusText = {
    new: "New",
    acknowledged: "Acknowledged",
    resolved: "Resolved",
    "false-positive": "False Positive",
  }

  const textColor = {
    new: "text-gray-300",
    acknowledged: "text-green-400",
    resolved: "text-green-400",
    "false-positive": "text-gray-500",
  }

  return (
    <span
      className={`px-2 py-1 text-xs rounded-full bg-gray-800 ${textColor[status]}`}
      aria-label={`Status: ${statusText[status]}`}
    >
      {statusText[status]}
    </span>
  )
}
