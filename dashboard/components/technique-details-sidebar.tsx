"use client"

import { AlertCircle, ExternalLink, X } from "lucide-react"
import { Card } from "@/components/card"
import { TechniqueMetrics } from "@/components/technique-metrics"
import { TechniqueDescription } from "@/components/technique-description"
import { TechniqueDetection } from "@/components/technique-detection"
import { TechniqueMitigation } from "@/components/technique-mitigation"
import type { Node } from "@/utils/attack-graph-data"
import type { TechniqueDetails } from "@/lib/api-client"

interface TechniqueDetailsSidebarProps {
  isVisible: boolean
  selectedTechnique: Node | null
  techniqueDetails: TechniqueDetails | null
  onClose: () => void
}

export function TechniqueDetailsSidebar({
  isVisible,
  selectedTechnique,
  techniqueDetails,
  onClose,
}: TechniqueDetailsSidebarProps) {
  return (
    <div className={`w-full lg:w-80 transition-all duration-300 ${isVisible ? "opacity-100" : "hidden"}`}>
      <Card className="h-full overflow-y-auto max-h-[80vh]">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">Technique Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-blue-400 transition-colors"
            aria-label="Close details panel"
          >
            <X size={20} />
          </button>
        </div>

        {!selectedTechnique || !techniqueDetails ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <AlertCircle size={32} className="text-gray-600 mb-4" />
            <p className="text-gray-400">Select a node to view details</p>
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <p className="text-gray-400 text-sm mb-1">MITRE ATT&CK Technique</p>
              <h3 className="text-2xl font-bold text-white mb-1">{selectedTechnique.id}</h3>
              <p className="text-gray-300">{selectedTechnique.name}</p>
            </div>

            <TechniqueMetrics
              type={selectedTechnique.type}
              probability={selectedTechnique.probability}
              platforms={techniqueDetails.platforms}
              tactics={techniqueDetails.tactics}
            />

            <TechniqueDescription description={techniqueDetails.description} />

            <TechniqueDetection detection={techniqueDetails.detection} />

            <TechniqueMitigation mitigation={techniqueDetails.mitigation} />

            <a
              href={`https://attack.mitre.org/techniques/${selectedTechnique.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors border-t border-slate-700 mt-6 pt-6"
            >
              View on MITRE ATT&CK
              <ExternalLink size={16} />
            </a>
          </div>
        )}
      </Card>
    </div>
  )
}
