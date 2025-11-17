export function LoadingSpinner({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12">
      <div className="relative w-16 h-16">
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
      </div>
      <p className="mt-4 text-gray-400 text-sm">{message}</p>
    </div>
  )
}
