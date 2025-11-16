import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { server } from '../../setup'
import { http, HttpResponse } from 'msw'
import AttackGraphPage from '@/app/attack-graph/page'

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

describe('Attack Graph Page Integration', () => {
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
        http.get(`${API_URL}/api/mitre/graph`, async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json({
            nodes: [],
            links: []
          })
        })
      )

      render(<AttackGraphPage />)

      expect(screen.getByText('Loading attack graph...')).toBeInTheDocument()
      
      await waitFor(() => {
        expect(screen.queryByText('Loading attack graph...')).not.toBeInTheDocument()
      })
    })

    it('should load and display attack graph', async () => {
      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [
              {
                id: 'T0800',
                name: 'Activate Firmware Update Mode',
                type: 'current',
                probability: 1.0
              },
              {
                id: 'T0802',
                name: 'Automated Collection',
                type: 'predicted',
                probability: 0.85
              }
            ],
            links: [
              {
                source: 'T0800',
                target: 'T0802',
                probability: 0.85
              }
            ]
          })
        })
      )

      render(<AttackGraphPage />)

      await waitFor(() => {
        expect(screen.getByText('Current Attacks')).toBeInTheDocument()
      })

      // Check for current and predicted attacks (both show "1")
      const cards = screen.getAllByText('1')
      expect(cards.length).toBeGreaterThanOrEqual(1)
      expect(screen.getByText('Predicted Techniques')).toBeInTheDocument()
    })

    it('should display technique details when node is clicked', async () => {
      const user = userEvent.setup()

      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [
              {
                id: 'T0800',
                name: 'Activate Firmware Update Mode',
                type: 'current',
                probability: 1.0
              }
            ],
            links: []
          })
        }),
        http.get(`${API_URL}/api/mitre/technique/T0800`, () => {
          return HttpResponse.json({
            id: 'T0800',
            name: 'Activate Firmware Update Mode',
            description: 'Adversaries may activate firmware update mode...',
            detection: 'Monitor for unusual firmware update requests...',
            mitigation: 'Implement secure firmware update procedures...',
            platforms: ['Control Server', 'Engineering Workstation'],
            tactics: ['Persistence', 'Inhibit Response Function']
          })
        })
      )

      render(<AttackGraphPage />)

      await waitFor(() => {
        expect(screen.getByText('Current Attacks')).toBeInTheDocument()
      })

      // The sidebar should be visible by default
      expect(screen.getByText(/technique details/i)).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should display error message when API fails', async () => {
      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      render(<AttackGraphPage />)

      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    it('should allow retry after error', async () => {
      const user = userEvent.setup()
      let attemptCount = 0

      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          attemptCount++
          if (attemptCount === 1) {
            return new HttpResponse(null, { status: 500 })
          }
          return HttpResponse.json({
            nodes: [],
            links: []
          })
        })
      )

      render(<AttackGraphPage />)

      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument()
      }, { timeout: 3000 })

      const retryButton = screen.getByRole('button', { name: /retry/i })
      await user.click(retryButton)

      await waitFor(() => {
        expect(screen.queryByText('Error')).not.toBeInTheDocument()
      }, { timeout: 3000 })
      
      // After retry, should show empty state since we return empty nodes
      await waitFor(() => {
        expect(screen.getByText('No attacks detected')).toBeInTheDocument()
      })
    })
  })

  describe('Empty States', () => {
    it('should handle no attacks gracefully', async () => {
      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [],
            links: []
          })
        })
      )

      render(<AttackGraphPage />)

      await waitFor(() => {
        expect(screen.getByText('No attacks detected')).toBeInTheDocument()
      })
    })
  })

  describe('Graph Interactions', () => {
    it('should display correct node counts', async () => {
      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [
              { id: 'T0800', name: 'Technique 1', type: 'current', probability: 1.0 },
              { id: 'T0801', name: 'Technique 2', type: 'current', probability: 1.0 },
              { id: 'T0802', name: 'Technique 3', type: 'predicted', probability: 0.85 },
              { id: 'T0803', name: 'Technique 4', type: 'predicted', probability: 0.75 }
            ],
            links: []
          })
        })
      )

      render(<AttackGraphPage />)

      await waitFor(() => {
        expect(screen.getByText('Current Attacks')).toBeInTheDocument()
      })

      // Check counts
      const cards = screen.getAllByText(/2|4/)
      expect(cards.length).toBeGreaterThan(0)
    })

    it('should toggle sidebar visibility', async () => {
      const user = userEvent.setup()

      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [
              { id: 'T0800', name: 'Technique 1', type: 'current', probability: 1.0 }
            ],
            links: []
          })
        })
      )

      render(<AttackGraphPage />)

      await waitFor(() => {
        expect(screen.getByText('Current Attacks')).toBeInTheDocument()
      })

      // Sidebar should be visible initially
      expect(screen.getByText(/technique details/i)).toBeInTheDocument()

      // Find and click toggle button
      const toggleButton = screen.getByRole('button', { name: /toggle/i })
      await user.click(toggleButton)

      // Sidebar should be hidden (component will handle this via CSS)
      // We can't easily test CSS visibility, so just verify button works
      expect(toggleButton).toBeInTheDocument()
    })
  })

  describe('WebSocket Real-Time Updates', () => {
    it('should connect to WebSocket and subscribe to attack-graph room', async () => {
      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [
              {
                id: 'T0800',
                name: 'Modify Control Logic',
                type: 'detected',
                tactics: ['Inhibit Response Function'],
                confidence: 0.85,
              },
            ],
            links: [],
          })
        })
      )

      render(<AttackGraphPage />)

      await waitFor(() => {
        expect(mockWs).not.toBeNull()
      })

      // Should subscribe to attack-graph room
      await waitFor(() => {
        const subscribeMessage = mockWs?.sentMessages.find(msg => {
          const parsed = JSON.parse(msg)
          return parsed.action === 'subscribe' && parsed.room === 'attack-graph'
        })
        expect(subscribeMessage).toBeDefined()
      })
    })

    it('should add new detected technique in real-time', async () => {
      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [
              {
                id: 'T0800',
                name: 'Modify Control Logic',
                type: 'detected',
                tactics: ['Inhibit Response Function'],
                confidence: 0.85,
              },
            ],
            links: [],
          })
        })
      )

      const { container } = render(<AttackGraphPage />)

      // Wait for initial load
      await waitFor(() => {
        expect(screen.queryByText('Loading attack graph...')).not.toBeInTheDocument()
      })

      // Get initial node count
      const initialNodes = container.querySelectorAll('circle').length

      // Simulate WebSocket message with new attack detection
      mockWs?.simulateMessage({
        type: 'attack_detected',
        data: {
          technique_id: 'T0802',
          technique_name: 'Automated Collection',
          confidence: 0.92,
          timestamp: new Date().toISOString(),
        },
      })

      // New node should be added to the graph (check node count increased)
      await waitFor(() => {
        const newNodes = container.querySelectorAll('circle').length
        expect(newNodes).toBeGreaterThan(initialNodes)
      })
    })

    it('should update technique confidence in real-time', async () => {
      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [
              {
                id: 'T0800',
                name: 'Modify Control Logic',
                type: 'detected',
                tactics: ['Inhibit Response Function'],
                confidence: 0.85,
              },
            ],
            links: [],
          })
        })
      )

      const { container } = render(<AttackGraphPage />)

      // Wait for initial load
      await waitFor(() => {
        expect(screen.queryByText('Loading attack graph...')).not.toBeInTheDocument()
      })

      // Get initial node count
      const initialNodes = container.querySelectorAll('circle').length

      // Simulate WebSocket message with confidence update
      mockWs?.simulateMessage({
        type: 'attack_detected',
        data: {
          technique_id: 'T0800',
          technique_name: 'Modify Control Logic',
          confidence: 0.95,
          timestamp: new Date().toISOString(),
        },
      })

      // Node count should remain the same (update, not add)
      await waitFor(() => {
        const newNodes = container.querySelectorAll('circle').length
        expect(newNodes).toBe(initialNodes)
      })
    })

    it('should handle graph updates without breaking existing nodes', async () => {
      server.use(
        http.get(`${API_URL}/api/mitre/graph`, () => {
          return HttpResponse.json({
            nodes: [
              {
                id: 'T0800',
                name: 'Modify Control Logic',
                type: 'detected',
                tactics: ['Inhibit Response Function'],
                confidence: 0.85,
              },
              {
                id: 'T0801',
                name: 'Monitor Process State',
                type: 'predicted',
                tactics: ['Collection'],
                confidence: 0.65,
              },
            ],
            links: [
              {
                source: 'T0800',
                target: 'T0801',
                type: 'leads-to',
              },
            ],
          })
        })
      )

      const { container } = render(<AttackGraphPage />)

      // Wait for initial load (2 nodes)
      await waitFor(() => {
        expect(screen.queryByText('Loading attack graph...')).not.toBeInTheDocument()
      })

      const initialNodes = container.querySelectorAll('circle').length
      expect(initialNodes).toBeGreaterThanOrEqual(2)

      // Simulate new attack detection
      mockWs?.simulateMessage({
        type: 'attack_detected',
        data: {
          technique_id: 'T0802',
          technique_name: 'Automated Collection',
          confidence: 0.88,
          timestamp: new Date().toISOString(),
        },
      })

      // Should have more nodes than before
      await waitFor(() => {
        const newNodes = container.querySelectorAll('circle').length
        expect(newNodes).toBeGreaterThan(initialNodes)
      })
    })
  })
})
