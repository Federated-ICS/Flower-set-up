import { FileX } from "lucide-react"

interface EmptyStateProps {
  title?: string
  message?: string
}

export function EmptyState({ 
  title = "No data found", 
  message = "There are no items to display." 
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <FileX className="w-16 h-16 text-gray-600 mb-4" />
      <h3 className="text-xl font-semibold text-gray-400 mb-2">{title}</h3>
      <p className="text-gray-500 text-sm max-w-md">{message}</p>
    </div>
  )
}
