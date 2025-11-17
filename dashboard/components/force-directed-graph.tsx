"use client"

import type React from "react"

import { useEffect, useRef, useImperativeHandle, forwardRef } from "react"
import * as d3 from "d3"
import type { Node, Link } from "@/utils/attack-graph-data"

interface ForceDirectedGraphProps {
  nodes: Node[]
  links: Link[]
  onNodeClick: (node: Node) => void
  containerRef: React.RefObject<HTMLDivElement | null>
}

export interface ForceDirectedGraphHandle {
  resetView: () => void
}

export const ForceDirectedGraph = forwardRef<ForceDirectedGraphHandle, ForceDirectedGraphProps>(
  ({ nodes, links, onNodeClick, containerRef }, ref) => {
    const svgRef = useRef<SVGSVGElement>(null)
    const gNodeRef = useRef<SVGGElement>(null)
    const simulationRef = useRef<d3.Simulation<Node, Link> | null>(null)
    const selectedNodeRef = useRef<string | null>(null)

    useImperativeHandle(ref, () => ({
      resetView: () => {
        if (gNodeRef.current) {
          d3.select(gNodeRef.current).transition().duration(750).attr("transform", "translate(0,0) scale(1)")
        }
      },
    }))

    useEffect(() => {
      if (!svgRef.current || !containerRef.current || nodes.length === 0) return

      const width = containerRef.current.clientWidth
      const height = 600

      // Clear previous SVG
      d3.select(svgRef.current).selectAll("*").remove()

      // Create SVG
      const svg = d3
        .select(svgRef.current)
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("aria-label", "Attack graph visualization showing MITRE ATT&CK techniques")

      // Create force simulation
      const simulation = d3
        .forceSimulation<Node>(nodes)
        .force(
          "link",
          d3
            .forceLink<Node, Link>(links)
            .id((d) => d.id)
            .distance(150),
        )
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide(40))

      simulationRef.current = simulation

      // Create groups for links and nodes
      const g = svg.append("g").attr("class", "graph-group")
      gNodeRef.current = g.node() as SVGGElement

      // Add zoom behavior
      const zoom = d3.zoom<SVGSVGElement, unknown>().on("zoom", (event) => {
        g.attr("transform", event.transform)
      })

      svg.call(zoom)

      // Draw links
      const link = g
        .selectAll("line")
        .data(links)
        .enter()
        .append("line")
        .attr("stroke", "#3b82f6")
        .attr("stroke-opacity", (d) => d.probability * 0.8)
        .attr("stroke-width", 2)

      // Draw nodes
      const node = g
        .selectAll("circle")
        .data(nodes)
        .enter()
        .append("circle")
        .attr("r", 20)
        .attr("fill", "#1e293b")
        .attr("stroke-width", (d) => (d.type === "current" ? 3 : 2))
        .attr("stroke", (d) => (d.type === "current" ? "#ef4444" : "#f59e0b"))
        .attr("class", (d) => `${d.type}-node`)
        .attr("cursor", "pointer")
        .call(
          d3
            .drag<SVGCircleElement, Node>()
            .on("start", (event, d) => {
              d.fx = d.x
              d.fy = d.y
              simulation.alpha(0.3).restart()
            })
            .on("drag", (event, d) => {
              d.fx = event.x
              d.fy = event.y
            })
            .on("end", (event, d) => {
              d.fx = null
              d.fy = null
            }),
        )
        .on("click", (event, d) => {
          event.stopPropagation()
          selectedNodeRef.current = d.id
          node.attr("stroke-width", (node) => (node.id === d.id ? 3 : node.type === "current" ? 3 : 2))
          onNodeClick(d)
        })

      // Add labels
      const labels = g
        .selectAll("text")
        .data(nodes)
        .enter()
        .append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "0.3em")
        .attr("font-size", "10px")
        .attr("fill", "#e5e7eb")
        .attr("pointer-events", "none")
        .text((d) => d.id)

      // Update on simulation tick
      simulation.on("tick", () => {
        link
          .attr("x1", (d) => (typeof d.source === "object" ? d.source.x || 0 : 0))
          .attr("y1", (d) => (typeof d.source === "object" ? d.source.y || 0 : 0))
          .attr("x2", (d) => (typeof d.target === "object" ? d.target.x || 0 : 0))
          .attr("y2", (d) => (typeof d.target === "object" ? d.target.y || 0 : 0))

        node.attr("cx", (d) => d.x || 0).attr("cy", (d) => d.y || 0)

        labels.attr("x", (d) => d.x || 0).attr("y", (d) => d.y || 0)
      })

      // Cleanup
      return () => {
        if (simulationRef.current) {
          simulationRef.current.stop()
        }
      }
    }, [nodes, links, onNodeClick, containerRef])

    return <svg ref={svgRef} className="w-full" />
  },
)

ForceDirectedGraph.displayName = "ForceDirectedGraph"
