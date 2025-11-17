"use client"

import type React from "react"

interface PrivacyMetricCardProps {
  title: string
  icon: React.ReactNode
  iconColor: string
  mainValue: string
  mainLabel: string
  secondaryValue: string
  secondaryLabel: string
}

export function PrivacyMetricCard({
  title,
  icon,
  iconColor,
  mainValue,
  mainLabel,
  secondaryValue,
  secondaryLabel,
}: PrivacyMetricCardProps) {
  return (
    <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        <div className={iconColor}>{icon}</div>
      </div>

      <div className="flex justify-between items-end">
        <div>
          <p className="text-2xl font-bold text-white">{mainValue}</p>
          <p className="text-sm text-gray-400">{mainLabel}</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-medium text-gray-300">{secondaryValue}</p>
          <p className="text-xs text-gray-500">{secondaryLabel}</p>
        </div>
      </div>
    </div>
  )
}
