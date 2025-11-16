"use client"

import { useState, useRef, useCallback, useEffect } from "react"
import { Footer } from "@/components/footer"
import { VantaBackground } from "@/components/vanta-background"
import { AttackGraphHeader } from "@/components/attack-graph-header"
import { ForceDirectedGraph, type ForceDirectedGraphHandle } from "@/components/force-directed-graph"
import { TechniqueDetailsSidebar } from "@/components/technique-details-sidebar"
import { AttackTimeline } from "@/components/attack-timeline"
import { Card } from "@/components/card"
import { LoadingSpinner } from "@/components/loading-spinner"
import { ErrorMessage } from "@/components/error-message"
import { apiClient, type TechniqueDetails } from "@/lib/api-client"
import { useWebSocket } from "@/lib/useWebSocket"
import type { Node, Link } from "@/utils/attack-graph-data"

export default function AttackGraphPage() {
  const graphContainerRef = useRef<HTMLDivElement>(null)
  const graphRef = useRef<ForceDirectedGraphHandle>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [techniqueDetails, setTechniqueDetails] = useState<TechniqueDetails | null>(null)
  const [isSidebarVisible, setIsSidebarVisible] = useState(true)
  const [graphData, setGraphData] = useState<{ nodes: Node[]; links: Link[] } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // WebSocket connection for real-time updates
  const { lastMessage, subscribe, isConnected } = useWebSocket({
    autoConnect: true,
  })

  // Fetch attack graph data
  const fetchGraphData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await apiClient.getAttackGraph()
      setGraphData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch attack graph")
    } finally {
      setLoading(false)
    }
  }, [])

  // Fetch data on mount
  useEffect(() => {
    fetchGraphData()
  }, [fetchGraphData])

  // Subscribe to attack-graph room when WebSocket connects
  useEffect(() => {
    if (isConnected) {
      subscribe('attack-graph')
    }
  }, [isConnected, subscribe])

  // Handle WebSocket messages for real-time attack detections
  useEffect(() => {
    if (!lastMessage) return

    if (lastMessage.type === 'attack_detected') {
      const data = lastMessage.data

      if (data?.technique_id) {
        setGraphData(prev => {
          if (!prev) return prev
          
          // Check if technique already exists
          const existingNode = prev.nodes.find(n => n.id === data.technique_id)

          if (existingNode) {
            // Update existing node confidence/probability and type
            return {
              ...prev,
              nodes: prev.nodes.map(node =>
                node.id === data.technique_id
                  ? { 
                      ...node, 
                      probability: data.confidence ?? data.probability ?? node.probability,
                      type: data.type || node.type // Update type if provided
                    }
                  : node
              ),
              links: prev.links, // Keep existing links
            }
          } else {
            // Add new detected technique
            const newNode: Node = {
              id: data.technique_id,
              name: data.technique_name || data.technique_id,
              type: data.type || 'current', // Use provided type or default to 'current'
              probability: data.confidence ?? data.probability ?? 0.5,
            }

            // Handle links if provided
            const newLinks: Link[] = []
            
            // Add link from source technique if provided
            if (data.source_technique_id) {
              newLinks.push({
                source: data.source_technique_id,
                target: data.technique_id,
                probability: data.link_probability ?? data.confidence ?? 0.5,
              })
            }
            
            // Add multiple links if provided
            if (data.links && Array.isArray(data.links)) {
              data.links.forEach((link: any) => {
                newLinks.push({
                  source: link.source,
                  target: link.target,
                  probability: link.probability ?? 0.5,
                })
              })
            }

            return {
              ...prev,
              nodes: [...prev.nodes, newNode],
              links: [...prev.links, ...newLinks],
            }
          }
        })
      }
    }
  }, [lastMessage])

  // Fetch technique details when node is selected
  useEffect(() => {
    if (selectedNode) {
      apiClient.getTechniqueDetails(selectedNode.id)
        .then(setTechniqueDetails)
        .catch(console.error)
    }
  }, [selectedNode])

  const handleNodeClick = useCallback((node: Node) => {
    setSelectedNode(node)
  }, [])

  const handleResetView = useCallback(() => {
    if (graphRef.current) {
      graphRef.current.resetView()
    }
  }, [])

  const handleToggleSidebar = useCallback(() => {
    setIsSidebarVisible((prev) => !prev)
  }, [])

  const handleCloseSidebar = useCallback(() => {
    setIsSidebarVisible(false)
  }, [])

  const handleRetry = useCallback(() => {
    fetchGraphData()
  }, [fetchGraphData])

  // Render loading state
  if (loading) {
    return (
      <>
        <VantaBackground />
        <div className="min-h-screen flex flex-col">
          <main className="flex-1 container mx-auto px-4 py-8">
            <LoadingSpinner message="Loading attack graph..." />
          </main>
          <Footer />
        </div>
      </>
    )
  }

  // Render error state
  if (error) {
    return (
      <>
        <VantaBackground />
        <div className="min-h-screen flex flex-col">
          <main className="flex-1 container mx-auto px-4 py-8">
            <ErrorMessage message={error} onRetry={handleRetry} />
          </main>
          <Footer />
        </div>
      </>
    )
  }

  // Render empty state
  if (!graphData || graphData.nodes.length === 0) {
    return (
      <>
        <VantaBackground />
        <div className="min-h-screen flex flex-col">
          <main className="flex-1 container mx-auto px-4 py-8">
            <AttackGraphHeader onResetView={handleResetView} onToggleSidebar={handleToggleSidebar} />
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">No attacks detected</p>
            </div>
          </main>
          <Footer />
        </div>
      </>
    )
  }

  const currentAttacks = graphData.nodes.filter((n) => n.type === "current").length
  const predictedAttacks = graphData.nodes.filter((n) => n.type === "predicted").length

  return (
    <>
      <VantaBackground />
      <div className="min-h-screen flex flex-col">
        <main className="flex-1 container mx-auto px-4 py-8">
          <AttackGraphHeader onResetView={handleResetView} onToggleSidebar={handleToggleSidebar} />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <Card glowEffect>
              <h2 className="text-sm text-gray-400 mb-2">Current Attacks</h2>
              <p className="text-4xl font-mono font-bold text-red-400">{currentAttacks}</p>
            </Card>

            <Card>
              <h2 className="text-sm text-gray-400 mb-2">Predicted Techniques</h2>
              <p className="text-4xl font-mono font-bold text-yellow-400">{predictedAttacks}</p>
            </Card>

            <Card>
              <h2 className="text-sm text-gray-400 mb-2">Total Nodes</h2>
              <p className="text-4xl font-mono font-bold text-blue-400">{graphData.nodes.length}</p>
            </Card>
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            <div ref={graphContainerRef} className="flex-1 rounded-lg border border-slate-700 bg-slate-900/50">
              <ForceDirectedGraph
                ref={graphRef}
                nodes={graphData.nodes}
                links={graphData.links}
                onNodeClick={handleNodeClick}
                containerRef={graphContainerRef}
              />
            </div>

            <TechniqueDetailsSidebar
              isVisible={isSidebarVisible}
              selectedTechnique={selectedNode}
              techniqueDetails={techniqueDetails}
              onClose={handleCloseSidebar}
            />
          </div>

          <div className="mt-8">
            <AttackTimeline
              nodes={graphData.nodes}
              selectedNodeId={selectedNode?.id || null}
              onNodeClick={handleNodeClick}
            />
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
}
