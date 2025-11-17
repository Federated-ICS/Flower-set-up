"use client"

interface FLFooterProps {
  lastRoundStartTime: Date
}

export function FLFooter({ lastRoundStartTime }: FLFooterProps) {
  return (
    <footer className="border-t border-slate-700 pt-6 mt-8 text-center text-sm text-gray-400">
      <div className="space-y-2">
        <p>© 2023 OSB Watchtower</p>
        <p>
          Last FL round started: <span className="font-mono">{lastRoundStartTime.toLocaleString()}</span>
        </p>
      </div>
    </footer>
  )
}
