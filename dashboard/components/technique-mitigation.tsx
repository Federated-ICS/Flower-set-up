"use client"

import { Shield } from "lucide-react"

interface TechniqueMitigationProps {
  mitigation?: string
}

export function TechniqueMitigation({ mitigation }: TechniqueMitigationProps) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <Shield size={16} className="text-blue-400" />
        <h3 className="font-semibold text-white">Mitigation</h3>
      </div>
      <div className="bg-gray-800 rounded-md p-3 text-sm text-gray-300">
        {mitigation || "No mitigation information available."}
      </div>
    </div>
  )
}
