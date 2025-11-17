import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { server } from '../../setup'
import { http, HttpResponse } from 'msw'
import DashboardPage from '@/app/page'

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

  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', {
        data: JSON.stringify(data)
      }))
    }
  }
}

let mockWs: MockWebSocket | null = null

describe('Dashboard Page Integration', () => {
  const API_URL = 'http://localhost:8000'

  beforeEach(() => {
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
    it('should display loading state initially', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json({
            total: 12,
            critical: 3,
            unresolved: 8,
            false_positives: 1,
          })
        }),
        http.get(`${API_URL}/api/alerts`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      expect(screen.getByText('Loading dashboard...')).toBeInTheDocument()
      
      await waitFor(() => {
        expect(screen.queryByText('Loading dashboard...')).not.toBeInTheDocument()
      })
    })

    it('should load and display system status', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 12,
            critical: 3,
            unresolved: 8,
            false_positives: 1,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('System Status')).toBeInTheDocument()
      })

      // Check that unresolved alerts count is displayed
      expect(screen.getByText('8')).toBeInTheDocument()
    })

    it('should load and display recent alerts', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 12,
            critical: 3,
            unresolved: 8,
            false_positives: 1,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [
              {
                id: '1',
                title: 'Suspicious Login Attempt',
                description: 'Multiple failed login attempts detected',
                severity: 'critical',
                facility_id: 'facility_a',
                status: 'new',
                timestamp: '2024-01-15T10:00:00Z',
                sources: [],
              },
              {
                id: '2',
                title: 'Unusual Network Traffic',
                description: 'Abnormal traffic pattern detected',
                severity: 'high',
                facility_id: 'facility_b',
                status: 'new',
                timestamp: '2024-01-15T09:45:00Z',
                sources: [],
              },
            ],
            total: 2,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Recent Alerts')).toBeInTheDocument()
      })

      expect(screen.getByText('Suspicious Login Attempt')).toBeInTheDocument()
      expect(screen.getByText('Unusual Network Traffic')).toBeInTheDocument()
    })

    it('should load and display FL status when round is active', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 12,
            critical: 3,
            unresolved: 8,
            false_positives: 1,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json({
            id: 1,
            round_number: 42,
            status: 'in-progress',
            phase: 'training',
            progress: 67,
            epsilon: 0.5,
            model_accuracy: 89.5,
            clients: [],
            start_time: '2024-01-15T10:00:00Z',
          })
        }),
        http.get(`${API_URL}/api/fl/clients`, () => {
          return HttpResponse.json([
            {
              id: '1',
              name: 'Facility A',
              facility_id: 'facility_a',
              status: 'active',
              progress: 85,
              loss: 0.12,
              accuracy: 94.2,
              current_epoch: 8,
              total_epochs: 10,
            },
            {
              id: '2',
              name: 'Facility B',
              facility_id: 'facility_b',
              status: 'active',
              progress: 72,
              loss: 0.18,
              accuracy: 91.8,
              current_epoch: 7,
              total_epochs: 10,
            },
            {
              id: '3',
              name: 'Facility C',
              facility_id: 'facility_c',
              status: 'delayed',
              progress: 45,
              loss: 0.25,
              accuracy: 88.5,
              current_epoch: 4,
              total_epochs: 10,
            },
          ])
        })
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Federated Learning')).toBeInTheDocument()
      })

      expect(screen.getByText('Round #42')).toBeInTheDocument()
      // Check that 67% appears (multiple times is OK - in both System Status and FL Status)
      const progressTexts = screen.getAllByText('67%')
      expect(progressTexts.length).toBeGreaterThan(0)
    })

    it('should display no FL round message when no round is active', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 12,
            critical: 3,
            unresolved: 8,
            false_positives: 1,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Federated Learning')).toBeInTheDocument()
      })

      expect(screen.getByText('No active round')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should display error message when API fails', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return new HttpResponse(null, { status: 500 })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return new HttpResponse(null, { status: 500 })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    it('should allow retry after error', async () => {
      let attemptCount = 0

      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          attemptCount++
          if (attemptCount === 1) {
            return new HttpResponse(null, { status: 500 })
          }
          return HttpResponse.json({
            total: 12,
            critical: 3,
            unresolved: 8,
            false_positives: 1,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          if (attemptCount === 1) {
            return new HttpResponse(null, { status: 500 })
          }
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          if (attemptCount === 1) {
            return new HttpResponse(null, { status: 500 })
          }
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      // Wait for error
      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument()
      }, { timeout: 3000 })

      // Click retry
      const retryButton = screen.getByRole('button', { name: /retry/i })
      await retryButton.click()

      // Should show system status after successful retry
      await waitFor(() => {
        expect(screen.getByText('System Status')).toBeInTheDocument()
      }, { timeout: 3000 })

      // Error should be gone
      expect(screen.queryByText('Error')).not.toBeInTheDocument()
    })
  })

  describe('Empty States', () => {
    it('should handle no alerts gracefully', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 0,
            critical: 0,
            unresolved: 0,
            false_positives: 0,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Recent Alerts')).toBeInTheDocument()
      })

      expect(screen.getByText('No recent alerts')).toBeInTheDocument()
    })
  })

  describe('WebSocket Real-Time Updates', () => {
    it('should connect to WebSocket and subscribe to dashboard room', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 5,
            critical: 1,
            unresolved: 3,
            false_positives: 0,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(mockWs).not.toBeNull()
      })

      // Should subscribe to dashboard room
      await waitFor(() => {
        const subscribeMessage = mockWs?.sentMessages.find(msg => {
          const parsed = JSON.parse(msg)
          return parsed.action === 'subscribe' && parsed.room === 'dashboard'
        })
        expect(subscribeMessage).toBeDefined()
      })
    })

    it('should update alert stats in real-time', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 5,
            critical: 1,
            unresolved: 3,
            false_positives: 0,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('3')).toBeInTheDocument() // unresolved count
      })

      // Simulate WebSocket message with updated stats
      mockWs?.simulateMessage({
        type: 'dashboard_update',
        data: {
          alertStats: {
            total: 15,
            critical: 5,
            unresolved: 10,
            false_positives: 2,
          },
        },
      })

      // Stats should update
      await waitFor(() => {
        expect(screen.getByText('10')).toBeInTheDocument() // new unresolved count
      })
    })

    it('should update FL progress in real-time', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 5,
            critical: 1,
            unresolved: 3,
            false_positives: 0,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json({
            id: 1,
            round_number: 42,
            status: 'in-progress',
            phase: 'training',
            progress: 50,
            epsilon: 0.5,
            model_accuracy: 85.0,
            clients: [],
            start_time: '2024-01-15T10:00:00Z',
          })
        }),
        http.get(`${API_URL}/api/fl/clients`, () => {
          return HttpResponse.json([])
        })
      )

      render(<DashboardPage />)

      // Wait for initial FL status
      await waitFor(() => {
        expect(screen.getByText('Round #42')).toBeInTheDocument()
      })

      // Simulate WebSocket message with FL progress update
      mockWs?.simulateMessage({
        type: 'fl_progress',
        data: {
          round_number: 42,
          progress: 85,
          model_accuracy: 92.5,
        },
      })

      // Progress should update
      await waitFor(() => {
        expect(screen.getByText('85%')).toBeInTheDocument()
      })
    })

    it('should add new alerts to recent alerts list', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 1,
            critical: 0,
            unresolved: 1,
            false_positives: 0,
          })
        }),
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
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      // Wait for initial alert
      await waitFor(() => {
        expect(screen.getByText('Existing Alert')).toBeInTheDocument()
      })

      // Simulate new alert via WebSocket
      mockWs?.simulateMessage({
        type: 'alert_created',
        data: {
          id: '2',
          title: 'New Real-Time Alert',
          description: 'Test',
          severity: 'critical',
          facility_id: 'facility_b',
          status: 'new',
          timestamp: new Date().toISOString(),
          sources: [],
        },
      })

      // New alert should appear
      await waitFor(() => {
        expect(screen.getByText('New Real-Time Alert')).toBeInTheDocument()
      })
    })

    it('should handle alert_updated events from WebSocket', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 1,
            critical: 0,
            unresolved: 1,
            false_positives: 0,
          })
        }),
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
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      // Wait for initial alert
      await waitFor(() => {
        expect(screen.getByText('Test Alert')).toBeInTheDocument()
      })

      // Simulate alert update via WebSocket
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

      // Alert should still be visible (status update doesn't remove it)
      await waitFor(() => {
        expect(screen.getByText('Test Alert')).toBeInTheDocument()
      })
    })

    it('should handle attack_detected events from WebSocket', async () => {
      server.use(
        http.get(`${API_URL}/api/alerts/stats`, () => {
          return HttpResponse.json({
            total: 0,
            critical: 0,
            unresolved: 0,
            false_positives: 0,
          })
        }),
        http.get(`${API_URL}/api/alerts`, () => {
          return HttpResponse.json({
            alerts: [],
            total: 0,
            page: 1,
            pages: 1,
            limit: 3,
          })
        }),
        http.get(`${API_URL}/api/fl/rounds/current`, () => {
          return HttpResponse.json(null)
        })
      )

      render(<DashboardPage />)

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('System Status')).toBeInTheDocument()
      })

      // Simulate attack detected via WebSocket
      mockWs?.simulateMessage({
        type: 'attack_detected',
        data: {
          technique_id: 'T0800',
          name: 'Activate Firmware Update Mode',
          probability: 0.95,
          timestamp: new Date().toISOString(),
        },
      })

      // Dashboard should handle the event gracefully (no crash)
      // Note: Dashboard doesn't display attack details, but should not error
      await waitFor(() => {
        expect(screen.getByText('System Status')).toBeInTheDocument()
      })
    })
  })
})
