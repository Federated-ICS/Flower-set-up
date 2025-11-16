"use client"

import { useState, useEffect, useCallback } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { VantaBackground } from "@/components/vanta-background"
import { SystemStatusCard } from "@/components/system-status-card"
import { RecentAlertsCard } from "@/components/recent-alerts-card"
import { FLStatusCard } from "@/components/fl-status-card"
import { AttackPredictionCard } from "@/components/attack-prediction-card"
import { QuickActionsCard } from "@/components/quick-actions-card"
import { LoadingSpinner } from "@/components/loading-spinner"
import { ErrorMessage } from "@/components/error-message"
import { apiClient, type Alert, type AlertStats, type FLRound, type FLClient } from "@/lib/api-client"
import { useWebSocket } from "@/lib/useWebSocket"
import { formatDistanceToNow } from "date-fns"

export default function DashboardPage() {
  // State
  const [alertStats, setAlertStats] = useState<AlertStats | null>(null)
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([])
  const [currentRound, setCurrentRound] = useState<FLRound | null>(null)
  const [flClients, setFlClients] = useState<FLClient[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Attack prediction state (real-time via WebSocket)
  const [attackPrediction, setAttackPrediction] = useState({
    techniqueId: "T1190",
    techniqueName: "Exploit Public-Facing Application",
    confidence: 76,
    timelineProgress: 65,
  })

  // WebSocket connection for real-time updates
  const { lastMessage, subscribe, isConnected } = useWebSocket({
    autoConnect: true,
  })

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const [statsData, alertsResponse, roundData] = await Promise.all([
        apiClient.getAlertStats(),
        apiClient.getAlerts({ limit: 3 }),
        apiClient.getCurrentFLRound(),
      ])

      setAlertStats(statsData)
      setRecentAlerts(alertsResponse.alerts || [])
      setCurrentRound(roundData)

      // Fetch FL clients if there's an active round
      if (roundData) {
        const clientsData = await apiClient.getFLClients()
        setFlClients(clientsData)
      } else {
        setFlClients([])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch dashboard data")
    } finally {
      setLoading(false)
    }
  }, [])

  // Fetch data on mount
  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  // Subscribe to dashboard room when WebSocket connects
  useEffect(() => {
    if (isConnected) {
      console.log('🔔 Subscribing to dashboard room...')
      subscribe('dashboard')
      console.log('✅ Subscribed to dashboard room')
    }
  }, [isConnected, subscribe])

  // Handle WebSocket messages for real-time updates
  useEffect(() => {
    if (!lastMessage) return

    console.log('📬 WebSocket message received:', lastMessage)

    switch (lastMessage.type) {
      case 'dashboard_update':
        // Update alert stats if provided
        if (lastMessage.data?.alertStats) {
          setAlertStats(lastMessage.data.alertStats)
        }
        break

      case 'alert_created':
        // Add new alert to recent alerts (keep only top 3)
        if (lastMessage.data) {
          setRecentAlerts((prev) => {
            // Avoid duplicates
            if (prev.some((a) => a.id === lastMessage.data.id)) {
              return prev
            }
            return [lastMessage.data, ...prev].slice(0, 3)
          })
        }
        break

      case 'alert_updated':
        // Update existing alert in recent alerts list
        if (lastMessage.data) {
          setRecentAlerts((prev) => {
            return prev.map((alert) =>
              alert.id === lastMessage.data.id ? lastMessage.data : alert
            )
          })
        }
        break

      case 'fl_progress':
        // Update FL round progress
        console.log('📨 Received fl_progress event:', lastMessage.data)
        if (lastMessage.data) {
          setCurrentRound((prev) => {
            console.log('🔄 Current round before update:', prev)
            if (!prev) {
              // Create new round from event data if none exists
              console.log('✨ Creating new round from event data')
              return {
                id: lastMessage.data.round_id || lastMessage.data.id,
                round_number: lastMessage.data.round_number || 1,
                status: 'in-progress',
                phase: lastMessage.data.phase || 'training',
                progress: lastMessage.data.progress || 0,
                epsilon: lastMessage.data.epsilon || 0.5,
                model_accuracy: lastMessage.data.model_accuracy || 0,
                clients: [],
                start_time: new Date().toISOString(),
              }
            }
            const updated = {
              ...prev,
              progress: lastMessage.data.progress ?? prev.progress,
              model_accuracy: lastMessage.data.model_accuracy ?? prev.model_accuracy,
              phase: lastMessage.data.phase ?? prev.phase,
            }
            console.log('✅ Updated round:', updated)
            return updated
          })
          
          // Update facilities if included in the event
          if (lastMessage.data.clients && Array.isArray(lastMessage.data.clients)) {
            console.log('👥 Updating facilities:', lastMessage.data.clients.length)
            setFlClients(lastMessage.data.clients)
          }
        }
        break

      case 'attack_detected':
        // Update attack prediction card with real-time data
        if (lastMessage.data) {
          console.log('🎯 Attack detected:', lastMessage.data.technique_id)
          
          // Support both probability (0-1) and confidence (0-100) formats
          const confidence = lastMessage.data.confidence 
            ? (lastMessage.data.confidence > 1 ? lastMessage.data.confidence : lastMessage.data.confidence * 100)
            : (lastMessage.data.probability ? lastMessage.data.probability * 100 : 0)
          
          setAttackPrediction({
            techniqueId: lastMessage.data.technique_id || 'T0000',
            techniqueName: lastMessage.data.name || lastMessage.data.technique_name || 'Unknown Attack',
            confidence: Math.round(confidence),
            timelineProgress: Math.round(confidence), // Use confidence as timeline progress
          })
        }
        break
    }
  }, [lastMessage])

  const handleAction = (action: string) => {
    console.log("Action triggered:", action)
    // Action handling logic would go here
  }

  const handleRetry = useCallback(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  // Format alerts for RecentAlertsCard
  const formattedAlerts = (recentAlerts || []).map((alert) => ({
    id: alert.id,
    title: alert.title,
    severity: alert.severity,
    facility: alert.facility_id,
    timestamp: formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true }),
  }))

  // Format facilities for FLStatusCard
  const formattedFacilities = (flClients || []).slice(0, 3).map((client) => ({
    name: client.name,
    status: client.status,
  }))
  
  console.log('🏢 Formatted facilities for display:', formattedFacilities)

  // Render loading state
  if (loading) {
    return (
      <>
        <VantaBackground />
        <div className="min-h-screen flex flex-col">
          <Header />
          <main className="flex-1 container mx-auto px-4 py-8">
            <LoadingSpinner message="Loading dashboard..." />
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
          <Header />
          <main className="flex-1 container mx-auto px-4 py-8">
            <ErrorMessage message={error} onRetry={handleRetry} />
          </main>
          <Footer />
        </div>
      </>
    )
  }

  return (
    <>
      <VantaBackground />
      <div className="min-h-screen flex flex-col">
        <Header />

        <main className="flex-1 container mx-auto px-4 py-8">
          {/* System Status and Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <SystemStatusCard
              activeAlerts={alertStats?.unresolved || 0}
              flProgress={currentRound?.progress || 0}
              predictionAccuracy={currentRound?.model_accuracy || 0}
            />

            <RecentAlertsCard alerts={formattedAlerts} />

            {currentRound ? (
              <FLStatusCard
                roundNumber={currentRound.round_number}
                progress={currentRound.progress}
                facilities={formattedFacilities}
                epsilon={currentRound.epsilon || 0}
                delta="10⁻⁵"
              />
            ) : (
              <FLStatusCard
                roundNumber={0}
                progress={0}
                facilities={[]}
                epsilon={0}
                delta="10⁻⁵"
              />
            )}

            {/* Attack Prediction spans 2 columns on desktop */}
            <AttackPredictionCard
              techniqueId={attackPrediction.techniqueId}
              techniqueName={attackPrediction.techniqueName}
              confidence={attackPrediction.confidence}
              timelineProgress={attackPrediction.timelineProgress}
            />

            {/* Quick Actions */}
            <QuickActionsCard onAction={handleAction} />
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
}
