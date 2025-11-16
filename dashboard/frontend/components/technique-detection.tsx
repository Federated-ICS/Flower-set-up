"use client"

import { Eye } from "lucide-react"

interface TechniqueDetectionProps {
  detection?: string
}

export function TechniqueDetection({ detection }: TechniqueDetectionProps) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <Eye size={16} className="text-blue-400" />
        <h3 className="font-semibold text-white">Detection</h3>
      </div>
      <div className="bg-gray-800 rounded-md p-3 text-sm text-gray-300">
        {detection || "No detection information available."}
      </div>
    </div>
  )
}
