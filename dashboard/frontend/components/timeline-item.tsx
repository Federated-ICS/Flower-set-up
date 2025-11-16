"use client"

import type { Node } from "@/utils/attack-graph-data"

interface TimelineItemProps {
  node: Node
  isSelected: boolean
  onClick: (node: Node) => void
}

export function TimelineItem({ node, isSelected, onClick }: TimelineItemProps) {
  return (
    <button
      onClick={() => onClick(node)}
      className="flex flex-col items-center gap-2 cursor-pointer transition-all duration-300 hover:scale-110"
      aria-label={`${node.id}: ${node.name} (${node.type === "current" ? "Current" : "Predicted"})`}
    >
      <div
        className={`w-3 h-3 rounded-full transition-all ${
          node.type === "current" ? "bg-red-500" : "bg-blue-500"
        } ${isSelected ? "opacity-100 scale-125" : "opacity-40"}`}
      />
      <span className={`text-xs font-mono ${isSelected ? "text-blue-400" : "text-gray-400"}`}>{node.id}</span>
    </button>
  )
}
