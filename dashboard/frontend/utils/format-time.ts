// Format relative time utility
export function formatRelativeTime(timestamp: string): string {
  try {
    const date = new Date(timestamp)
    if (isNaN(date.getTime())) return "Invalid date"

    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 60) {
      return diffMins <= 1 ? "1 min ago" : `${diffMins} min ago`
    } else if (diffHours < 24) {
      return diffHours === 1 ? "1 hour ago" : `${diffHours} hours ago`
    } else if (diffDays < 7) {
      return diffDays === 1 ? "1 day ago" : `${diffDays} days ago`
    } else {
      return date.toLocaleDateString()
    }
  } catch {
    return "Unknown time"
  }
}

export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} min`
  }

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60

  if (hours < 24) {
    if (remainingMinutes === 0) {
      return `${hours} hour${hours > 1 ? "s" : ""}`
    }
    return `${hours}h ${remainingMinutes}m`
  }

  const days = Math.floor(hours / 24)
  return `${days} day${days > 1 ? "s" : ""}`
}

export function formatTimeRemaining(minutes: number): string {
  return `~${minutes} minutes`
}
