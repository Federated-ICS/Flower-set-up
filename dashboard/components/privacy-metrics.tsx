"use client"

import { Lock, Download, Shield } from "lucide-react"
import { Card } from "./card"
import { PrivacyMetricCard } from "./privacy-metric-card"

interface PrivacyMetricsProps {
  epsilon: number
  delta: string
  dataSize: string
  encryption: string
}

export function PrivacyMetrics({ epsilon, delta, dataSize, encryption }: PrivacyMetricsProps) {
  return (
    <Card>
      <h2 className="text-2xl font-semibold text-white mb-6">Privacy Metrics</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <PrivacyMetricCard
          title="Differential Privacy"
          icon={<Lock size={20} />}
          iconColor="text-green-400"
          mainValue={`ε = ${epsilon.toFixed(2)}`}
          mainLabel="Formal Guarantee"
          secondaryValue={`δ = ${delta}`}
          secondaryLabel="Epsilon/Delta"
        />

        <PrivacyMetricCard
          title="Data Transmission"
          icon={<Download size={20} />}
          iconColor="text-blue-400"
          mainValue="Weights Only"
          mainLabel="No Raw Data"
          secondaryValue={dataSize}
          secondaryLabel="Per Client"
        />

        <PrivacyMetricCard
          title="Security"
          icon={<Shield size={20} />}
          iconColor="text-purple-400"
          mainValue="Secure Aggregation"
          mainLabel="End-to-End"
          secondaryValue={encryption}
          secondaryLabel="Encryption"
        />
      </div>
    </Card>
  )
}
