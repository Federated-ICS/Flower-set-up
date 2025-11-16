"use client"

import { SeverityFilterButton } from "./severity-filter-button"

interface AlertFiltersProps {
  selectedSeverity: string
  selectedTimeRange: string
  selectedFacility: string
  onChange: (type: string, value: string) => void
}

export function AlertFilters({ selectedSeverity, selectedTimeRange, selectedFacility, onChange }: AlertFiltersProps) {
  return (
    <div className="space-y-4">
      {/* Severity Filters */}
      <div className="flex flex-wrap gap-2">
        <SeverityFilterButton
          label="All"
          severity="all"
          isActive={selectedSeverity === "all"}
          onClick={(val) => onChange("severity", val)}
        />
        <SeverityFilterButton
          label="Critical"
          severity="critical"
          isActive={selectedSeverity === "critical"}
          onClick={(val) => onChange("severity", val)}
        />
        <SeverityFilterButton
          label="High"
          severity="high"
          isActive={selectedSeverity === "high"}
          onClick={(val) => onChange("severity", val)}
        />
        <SeverityFilterButton
          label="Medium"
          severity="medium"
          isActive={selectedSeverity === "medium"}
          onClick={(val) => onChange("severity", val)}
        />
        <SeverityFilterButton
          label="Low"
          severity="low"
          isActive={selectedSeverity === "low"}
          onClick={(val) => onChange("severity", val)}
        />
      </div>

      {/* Time Range and Facility Dropdowns */}
      <div className="flex flex-col md:flex-row gap-4">
        <select
          value={selectedTimeRange}
          onChange={(e) => onChange("timeRange", e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option>Last 24 hours</option>
          <option>Last 7 days</option>
          <option>Last 30 days</option>
          <option>Custom range</option>
        </select>

        <select
          value={selectedFacility}
          onChange={(e) => onChange("facility", e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option>All Facilities</option>
          <option>Facility A</option>
          <option>Facility B</option>
          <option>Facility C</option>
        </select>
      </div>
    </div>
  )
}
