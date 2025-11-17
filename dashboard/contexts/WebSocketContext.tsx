/**
 * WebSocket Context Provider
 * Provides WebSocket connection to entire app
 */
'use client'

import React, { createContext, useContext, useEffect, ReactNode } from 'react'
import { useWebSocket, type UseWebSocketReturn } from '@/lib/useWebSocket'

interface WebSocketContextValue extends UseWebSocketReturn {
  // Add any additional context-specific methods here
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null)

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const websocket = useWebSocket({
    autoConnect: true,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
  })

  // Log connection status changes
  useEffect(() => {
    console.log(`WebSocket status: ${websocket.status}`)
  }, [websocket.status])

  return (
    <WebSocketContext.Provider value={websocket}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocketContext() {
  const context = useContext(WebSocketContext)
  
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider')
  }
  
  return context
}
