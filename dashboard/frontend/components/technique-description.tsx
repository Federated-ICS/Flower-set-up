"use client"

import { AlignLeft } from "lucide-react"

interface TechniqueDescriptionProps {
  description: string
}

export function TechniqueDescription({ description }: TechniqueDescriptionProps) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <AlignLeft size={16} className="text-blue-400" />
        <h3 className="font-semibold text-white">Description</h3>
      </div>
      <div className="bg-gray-800 rounded-md p-3 text-sm text-gray-300">{description}</div>
    </div>
  )
}
