"use client"

import { ClientCard } from "./client-card"

interface Client {
  id: string
  name: string
  status: "active" | "delayed" | "offline"
  progress: number
  loss: number
  accuracy: number
}

interface ClientStatusCardsProps {
  clients: Client[]
}

export function ClientStatusCards({ clients }: ClientStatusCardsProps) {
  return (
    <div className="space-y-4">
      {clients.map((client) => (
        <ClientCard
          key={client.id}
          name={client.name}
          status={client.status}
          progress={client.progress}
          loss={client.loss}
          accuracy={client.accuracy}
        />
      ))}
    </div>
  )
}
