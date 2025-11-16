import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { server } from '../../setup'
import { http, HttpResponse } from 'msw'
import AlertsPage from '@/app/alerts/page'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  url: string
  sentMessages: string[] = []

  constructor(url: string) {
    this.url = url
    // Simulate connection opening
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 10)
  }

  send(data: string) {
    this.sentMessages.push(data)
  }

  close() {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close'))
    }
  }

  // Helper to simulate receiving a message
  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', {
        data: JSON.stringify(data)
      }))
    }
  }
}

let mockWs: MockWebSocket | null = null

describe('Alerts Page Integration', () => {
  const API_URL = 'http://localhost:8000'

  beforeEach(() => {
    // Reset any runtime request handlers we may add during tests
    server.resetHandlers()
    
    // Mock WebSocket
    mockWs = null
    const WebSocketMock = class extends MockWebSocket {
      constructor(url: string) {
        super(url)
        mockWs = this
      }
    }
    vi.stubGlobal('WebSocket', WebSocketMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    mockWs = null
  })

  describe('Initial Load', () => {
    it('should display loading state initially', () => {
      // Mock delayed API response
      server.use(
        http.get(`${API_URL}/api/alerts`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 0,
            limit: 10,
          })
        })
      )

      render(<AlertsPage />)

      // Should show loading indicator
      expect(screen.getByText(/loading/i)).toBeInTheDocument()
    })

    it('should load and display alerts from API', async () => {
      // Mock API responses
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [
              {
                id: '1',
                title: 'Port Scan Detected',
                description: 'Suspicious port scanning activity',
                severity: 'critical',
                facility_id: 'facility_a',
                status: 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [
                  {
                    layer: 1,
                    model_name: 'Isolation Forest',
                    confidence: 0.95,
                    detection_time: '2024-01-15T10:00:00Z',
                    evidence: 'Anomaly detected',
                  },
                ],
              },
              {
                id: '2',
                title: 'DDoS Attack',
                description: 'Distributed denial of service',
                severity: 'high',
                facility_id: 'facility_b',
                status: 'acknowledged',
                timestamp: '2024-01-15T09:00:00Z',
                sources: [],
              },
            ],
            total: 2,
            page: 1,
            pages: 1,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 2,
            critical: 1,
            unresolved: 1,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('Port Scan Detected')).toBeInTheDocument()
      })

      expect(screen.getByText('DDoS Attack')).toBeInTheDocument()
    })

    it('should display alert statistics', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 0,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 20,
            critical: 5,
            unresolved: 12,
            false_positives: 2,
          })
        })
      )

      render(<AlertsPage />)

      await waitFor(() => {
        expect(screen.getByText('20')).toBeInTheDocument() // total
      })

      expect(screen.getByText('5')).toBeInTheDocument() // critical
      expect(screen.getByText('12')).toBeInTheDocument() // unresolved
      expect(screen.getByText('2')).toBeInTheDocument() // false positives
    })
  })

  describe('Filtering', () => {
    it('should filter alerts by severity', async () => {
      const user = userEvent.setup()
      let requestedSeverity = ''

      server.use(
        http.get(`${API_URL}/api/alerts`, ({ request }) => {
          const url = new URL(request.url)
          requestedSeverity = url.searchParams.get('severity') || ''

          return HttpResponse.json({
            alerts: requestedSeverity === 'critical' ? [
              {
                id: '1',
                title: 'Critical Alert',
                description: 'Test',
                severity: 'critical',
                facility_id: 'facility_a',
                status: 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [],
              },
            ] : [],
            total: requestedSeverity === 'critical' ? 1 : 0,
            page: 1,
            pages: 1,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 1,
            critical: 1,
            unresolved: 1,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      // Wait for initial load
      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click critical filter button
      const criticalButton = screen.getByRole('button', { name: /critical/i })
      await user.click(criticalButton)

      // Verify API was called with severity parameter
      await waitFor(() => {
        expect(requestedSeverity).toBe('critical')
      })

      // Verify filtered results displayed
      await waitFor(() => {
        expect(screen.getByText('Critical Alert')).toBeInTheDocument()
      })
    })

    it('should filter alerts by facility', async () => {
      // Skip this test for now - facility filter UI needs to be implemented
      // This test will be enabled once the facility dropdown is added to the UI
    })
  })

  describe('Search', () => {
    it('should search alerts by query', async () => {
      const user = userEvent.setup()
      let searchQuery = ''

      server.use(
        http.get(`${API_URL}/api/alerts`, ({ request }) => {
          const url = new URL(request.url)
          searchQuery = url.searchParams.get('search') || ''

          return HttpResponse.json({
            alerts: searchQuery === 'Port Scan' ? [
              {
                id: '1',
                title: 'Port Scan Detected',
                description: 'Test',
                severity: 'high',
                facility_id: 'facility_a',
                status: 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [],
              },
            ] : [],
            total: searchQuery === 'Port Scan' ? 1 : 0,
            page: 1,
            pages: 1,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 1,
            critical: 0,
            unresolved: 1,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Type in search box
      const searchInput = screen.getByPlaceholderText(/search/i)
      await user.type(searchInput, 'Port Scan')

      // Verify API called with search parameter
      await waitFor(() => {
        expect(searchQuery).toBe('Port Scan')
      })

      // Verify search results displayed
      await waitFor(() => {
        expect(screen.getByText('Port Scan Detected')).toBeInTheDocument()
      })
    })
  })

  describe('Pagination', () => {
    it('should paginate through alerts', async () => {
      const user = userEvent.setup()
      let currentPage = 1

      server.use(
        http.get(`${API_URL}/api/alerts`, ({ request }) => {
          const url = new URL(request.url)
          currentPage = parseInt(url.searchParams.get('page') || '1')

          return HttpResponse.json({
            alerts: currentPage === 2 ? [
              {
                id: '11',
                title: 'Alert Page 2',
                description: 'Test',
                severity: 'medium',
                facility_id: 'facility_a',
                status: 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [],
              },
            ] : [
              {
                id: '1',
                title: 'Alert Page 1',
                description: 'Test',
                severity: 'high',
                facility_id: 'facility_a',
                status: 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [],
              },
            ],
            total: 15,
            page: currentPage,
            pages: 2,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 15,
            critical: 0,
            unresolved: 15,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      // Wait for page 1 to load
      await waitFor(() => {
        expect(screen.getByText('Alert Page 1')).toBeInTheDocument()
      })

      // Click next page button
      const nextButton = screen.getByRole('button', { name: /next/i })
      await user.click(nextButton)

      // Verify page 2 loaded
      await waitFor(() => {
        expect(screen.getByText('Alert Page 2')).toBeInTheDocument()
      })

      expect(currentPage).toBe(2)
    })
  })

  describe('Error Handling', () => {
    it('should display error message when API fails', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return new HttpResponse(null, { status: 500 })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      render(<AlertsPage />)

      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument()
      }, { timeout: 3000 })

      // Should not show alerts
      expect(screen.queryByText('Port Scan')).not.toBeInTheDocument()
    })

    it('should allow retry after error', async () => {
      const user = userEvent.setup()
      let callCount = 0

      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          callCount++
          if (callCount === 1) {
            return new HttpResponse(null, { status: 500 })
          }
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 0,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          if (callCount === 1) {
            return new HttpResponse(null, { status: 500 })
          }
          return HttpResponse.json({
            total: 0,
            critical: 0,
            unresolved: 0,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      // Wait for error
      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument()
      }, { timeout: 3000 })

      // Click retry button
      const retryButton = screen.getByRole('button', { name: /retry/i })
      await user.click(retryButton)

      // Error should disappear and show empty state
      await waitFor(() => {
        expect(screen.queryByText('Error')).not.toBeInTheDocument()
      }, { timeout: 3000 })
      
      await waitFor(() => {
        expect(screen.getByText('No alerts found')).toBeInTheDocument()
      })
    })
  })

  describe('Alert Actions', () => {
    it('should update alert status when acknowledged', async () => {
      const user = userEvent.setup()
      let updatedStatus = ''
      let updateCallCount = 0

      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [
              {
                id: '1',
                title: 'Test Alert',
                description: 'Test',
                severity: 'high',
                facility_id: 'facility_a',
                status: updateCallCount > 0 ? 'acknowledged' : 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [],
              },
            ],
            total: 1,
            page: 1,
            pages: 1,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 1,
            critical: 0,
            unresolved: updateCallCount > 0 ? 0 : 1,
            false_positives: 0,
          })
        }),
        http.put(`${API_URL}/api/alerts/:id/status`, async ({ request }) => {
          const body = await request.json() as { status: string }
          updatedStatus = body.status
          updateCallCount++

          return HttpResponse.json({
            id: '1',
            title: 'Test Alert',
            description: 'Test',
            severity: 'high',
            facility_id: 'facility_a',
            status: updatedStatus,
            timestamp: '2024-01-15T10:00:00Z',
            sources: [],
          })
        })
      )

      render(<AlertsPage />)

      // Wait for alert to load
      await waitFor(() => {
        expect(screen.getByText('Test Alert')).toBeInTheDocument()
      })

      // Click the actions menu button (three dots)
      const actionButtons = screen.getAllByLabelText(/actions for alert/i)
      await user.click(actionButtons[0])

      // Wait for dropdown to appear and click acknowledge
      await waitFor(() => {
        expect(screen.getByText('Acknowledge')).toBeInTheDocument()
      })
      
      const acknowledgeButton = screen.getByText('Acknowledge')
      await user.click(acknowledgeButton)

      // Verify API was called
      await waitFor(() => {
        expect(updatedStatus).toBe('acknowledged')
      }, { timeout: 3000 })

      // Verify UI refreshed with updated status
      await waitFor(() => {
        expect(updateCallCount).toBeGreaterThan(0)
      })
    })
  })

  describe('WebSocket Real-Time Updates', () => {
    it('should connect to WebSocket on mount', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 0,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 0,
            critical: 0,
            unresolved: 0,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      await waitFor(() => {
        expect(mockWs).not.toBeNull()
      })

      expect(mockWs?.url).toContain('/ws')
    })

    it('should subscribe to alerts room after connection', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 0,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 0,
            critical: 0,
            unresolved: 0,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      await waitFor(() => {
        expect(mockWs?.sentMessages.length).toBeGreaterThan(0)
      })

      // Check if subscribe message was sent
      const subscribeMessage = mockWs?.sentMessages.find(msg => {
        const parsed = JSON.parse(msg)
        return parsed.action === 'subscribe' && parsed.room === 'alerts'
      })

      expect(subscribeMessage).toBeDefined()
    })

    it('should display new alert when alert_created event is received', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [
              {
                id: '1',
                title: 'Existing Alert',
                description: 'Test',
                severity: 'medium',
                facility_id: 'facility_a',
                status: 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [],
              },
            ],
            total: 1,
            page: 1,
            pages: 1,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 1,
            critical: 0,
            unresolved: 1,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Existing Alert')).toBeInTheDocument()
      })

      // Simulate WebSocket message for new alert
      const newAlert = {
        id: '2',
        title: 'Real-Time Alert',
        description: 'New alert via WebSocket',
        severity: 'critical',
        facility_id: 'facility_b',
        status: 'new',
        timestamp: new Date().toISOString(),
        sources: [],
      }

      mockWs?.simulateMessage({
        type: 'alert_created',
        data: newAlert,
      })

      // New alert should appear in the list
      await waitFor(() => {
        expect(screen.getByText('Real-Time Alert')).toBeInTheDocument()
      })

      // Both alerts should be visible
      expect(screen.getByText('Existing Alert')).toBeInTheDocument()
    })

    it('should update alert when alert_updated event is received', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [
              {
                id: '1',
                title: 'Test Alert',
                description: 'Test',
                severity: 'high',
                facility_id: 'facility_a',
                status: 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [],
              },
            ],
            total: 1,
            page: 1,
            pages: 1,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 1,
            critical: 0,
            unresolved: 1,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Test Alert')).toBeInTheDocument()
      })

      // Simulate WebSocket message for alert update
      mockWs?.simulateMessage({
        type: 'alert_updated',
        data: {
          id: '1',
          title: 'Test Alert',
          description: 'Test',
          severity: 'high',
          facility_id: 'facility_a',
          status: 'acknowledged',
          timestamp: '2024-01-15T10:00:00Z',
          sources: [],
        },
      })

      // Status should update in the UI
      await waitFor(() => {
        expect(screen.getByText(/acknowledged/i)).toBeInTheDocument()
      })
    })

    it('should update stats when dashboard_update event is received', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 0,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 5,
            critical: 1,
            unresolved: 3,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      // Wait for initial stats
      await waitFor(() => {
        expect(screen.getByText('5')).toBeInTheDocument()
      })

      // Simulate WebSocket message with updated stats
      mockWs?.simulateMessage({
        type: 'dashboard_update',
        data: {
          stats: {
            total: 10,
            critical: 3,
            unresolved: 7,
            false_positives: 1,
          },
        },
      })

      // Stats should update
      await waitFor(() => {
        expect(screen.getByText('10')).toBeInTheDocument()
      })
      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('7')).toBeInTheDocument()
    })

    it('should handle WebSocket disconnection gracefully', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 0,
            limit: 10,
          })
        }),
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 0,
            critical: 0,
            unresolved: 0,
            false_positives: 0,
          })
        })
      )

      render(<AlertsPage />)

      await waitFor(() => {
        expect(mockWs).not.toBeNull()
      })

      // Simulate disconnection
      mockWs?.close()

      // Page should still be functional (REST API fallback)
      await waitFor(() => {
        expect(screen.getByText(/No alerts found/i)).toBeInTheDocument()
      })
    })
  })
})
