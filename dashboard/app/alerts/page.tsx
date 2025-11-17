"use client"

import { useState, useCallback, useEffect } from "react"
import { Footer } from "@/components/footer"
import { VantaBackground } from "@/components/vanta-background"
import { AlertsHeader } from "@/components/alerts-header"
import { AlertFilters } from "@/components/alert-filters"
import { AlertStats } from "@/components/alert-stats"
import { AlertTable } from "@/components/alert-table"
import { Pagination } from "@/components/pagination"
import { LoadingSpinner } from "@/components/loading-spinner"
import { ErrorMessage } from "@/components/error-message"
import { EmptyState } from "@/components/empty-state"
import { apiClient, type Alert } from "@/lib/api-client"
import { useWebSocket } from "@/lib/useWebSocket"

const ITEMS_PER_PAGE = 10

interface AlertStats {
  total: number
  critical: number
  unresolved: number
  false_positives: number
}

export default function AlertsPage() {
  // State
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [stats, setStats] = useState<AlertStats>({ total: 0, critical: 0, unresolved: 0, false_positives: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(0)
  const [totalItems, setTotalItems] = useState(0)

  // Filters
  const [selectedSeverity, setSelectedSeverity] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTimeRange, setSelectedTimeRange] = useState("Last 30 days")
  const [selectedFacility, setSelectedFacility] = useState("All Facilities")
  const [currentPage, setCurrentPage] = useState(1)

  // WebSocket connection for real-time updates
  const { lastMessage, subscribe, isConnected } = useWebSocket({
    autoConnect: true,
  })

  // Fetch alerts from API
  const fetchAlerts = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      // Fetch alerts with filters
      const alertsResponse = await apiClient.getAlerts({
        severity: selectedSeverity !== "all" ? selectedSeverity : undefined,
        facility: selectedFacility !== "All Facilities" ? selectedFacility : undefined,
        search: searchQuery || undefined,
        time_range: selectedTimeRange,
        page: currentPage,
        limit: ITEMS_PER_PAGE,
      })

      // Fetch stats
      const statsResponse = await apiClient.getAlertStats()

      setAlerts(alertsResponse.alerts)
      setTotalPages(alertsResponse.pages)
      setTotalItems(alertsResponse.total)
      setStats(statsResponse)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch alerts")
    } finally {
      setLoading(false)
    }
  }, [selectedSeverity, selectedFacility, searchQuery, selectedTimeRange, currentPage])

  // Fetch data on mount and when filters change
  useEffect(() => {
    fetchAlerts()
  }, [fetchAlerts])

  // Subscribe to alerts room when WebSocket connects
  useEffect(() => {
    if (isConnected) {
      subscribe('alerts')
    }
  }, [isConnected, subscribe])

  // Handle WebSocket messages for real-time updates
  useEffect(() => {
    if (!lastMessage) return

    switch (lastMessage.type) {
      case 'alert_created':
        // Add new alert to the top of the list
        if (lastMessage.data) {
          setAlerts((prev) => {
            // Avoid duplicates
            if (prev.some((a) => a.id === lastMessage.data.id)) {
              return prev
            }
            return [lastMessage.data, ...prev]
          })
        }
        break

      case 'alert_updated':
        // Update existing alert
        if (lastMessage.data) {
          setAlerts((prev) =>
            prev.map((alert) =>
              alert.id === lastMessage.data.id ? lastMessage.data : alert
            )
          )
        }
        break

      case 'dashboard_update':
        // Update stats if provided
        if (lastMessage.data?.stats) {
          setStats(lastMessage.data.stats)
        }
        break
    }
  }, [lastMessage])

  // Event handlers
  const handleFilterChange = useCallback((type: string, value: string) => {
    if (type === "severity") setSelectedSeverity(value)
    if (type === "timeRange") setSelectedTimeRange(value)
    if (type === "facility") setSelectedFacility(value)
    setCurrentPage(1) // Reset to first page
  }, [])

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value)
    setCurrentPage(1) // Reset to first page
  }, [])

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page)
  }, [])

  const handleNewAlert = useCallback(() => {
    console.log("New alert creation requested")
    // TODO: Implement new alert creation
  }, [])

  const handleAlertAction = useCallback(async (alertId: string, action: string) => {
    try {
      await apiClient.updateAlertStatus(alertId, action)
      // Refresh alerts after update
      fetchAlerts()
    } catch (err) {
      console.error("Failed to update alert:", err)
    }
  }, [fetchAlerts])

  const handleRetry = useCallback(() => {
    fetchAlerts()
  }, [fetchAlerts])

  // Render loading state
  if (loading) {
    return (
      <>
        <VantaBackground />
        <div className="min-h-screen flex flex-col">
          <main className="flex-1 container mx-auto px-4 py-8">
            <AlertsHeader searchValue={searchQuery} onSearchChange={handleSearchChange} onNewAlert={handleNewAlert} />
            <LoadingSpinner message="Loading alerts..." />
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
            <AlertsHeader searchValue={searchQuery} onSearchChange={handleSearchChange} onNewAlert={handleNewAlert} />
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
        <main className="flex-1 container mx-auto px-4 py-8">
          <AlertsHeader searchValue={searchQuery} onSearchChange={handleSearchChange} onNewAlert={handleNewAlert} />

          <AlertFilters
            selectedSeverity={selectedSeverity}
            selectedTimeRange={selectedTimeRange}
            selectedFacility={selectedFacility}
            onChange={handleFilterChange}
          />

          <AlertStats
            totalAlerts={stats.total}
            critical={stats.critical}
            unresolved={stats.unresolved}
            falsePositives={stats.false_positives}
          />

          {alerts.length > 0 ? (
            <>
              <AlertTable alerts={alerts} onActionClick={handleAlertAction} />
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={totalItems}
                itemsPerPage={ITEMS_PER_PAGE}
                onPageChange={handlePageChange}
              />
            </>
          ) : (
            <EmptyState
              title="No alerts found"
              message="There are no alerts matching your current filters."
            />
          )}
        </main>

        <Footer />
      </div>
    </>
  )
}
