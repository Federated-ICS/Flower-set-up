"use client"

import { Card } from "@/components/card"
import { TimelineItem } from "@/components/timeline-item"
import type { Node } from "@/utils/attack-graph-data"

interface AttackTimelineProps {
  nodes: Node[]
  selectedNodeId: string | null
  onNodeClick: (node: Node) => void
}

export function AttackTimeline({ nodes, selectedNodeId, onNodeClick }: AttackTimelineProps) {
  return (
    <Card className="lg:col-span-3">
      <h2 className="text-xl font-semibold text-white mb-4">Attack Timeline</h2>
      <div className="flex overflow-x-auto space-x-4 pb-4">
        {nodes.map((node) => (
          <TimelineItem key={node.id} node={node} isSelected={selectedNodeId === node.id} onClick={onNodeClick} />
        ))}
      </div>
    </Card>
  )
}
