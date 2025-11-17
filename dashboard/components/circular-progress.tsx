"use client"

import { useEffect, useRef } from "react"

interface CircularProgressProps {
  progress: number
}

export function CircularProgress({ progress }: CircularProgressProps) {
  const circleRef = useRef<SVGCircleElement>(null)

  const radius = 15.9155
  const circumference = 2 * Math.PI * radius

  useEffect(() => {
    if (circleRef.current) {
      const offset = circumference * (1 - progress / 100)
      circleRef.current.style.strokeDashoffset = `${offset}`
    }
  }, [progress, circumference])

  return (
    <div className="flex items-center justify-center">
      <div className="relative w-40 h-40">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
          {/* Background circle */}
          <circle cx="18" cy="18" r={radius} fill="none" stroke="#1e293b" strokeWidth="2" />

          {/* Progress circle */}
          <circle
            ref={circleRef}
            cx="18"
            cy="18"
            r={radius}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="2"
            strokeDasharray={circumference}
            strokeDashoffset={circumference}
            strokeLinecap="round"
            style={{
              transition: "stroke-dashoffset 0.5s ease",
            }}
            aria-label={`Progress: ${progress}%`}
          />
        </svg>

        {/* Progress text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-3xl font-bold text-blue-400">{progress}%</span>
        </div>
      </div>
    </div>
  )
}
