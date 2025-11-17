import { AlertCircle, RefreshCw } from "lucide-react"

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12">
      <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-6 max-w-md w-full">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-red-400 font-semibold mb-1">Error</h3>
            <p className="text-red-300/80 text-sm">{message}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="mt-4 flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 rounded-md text-red-400 text-sm transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Retry
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
