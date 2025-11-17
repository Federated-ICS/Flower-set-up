"use client"

import { useEffect, useRef } from "react"

export function VantaBackground() {
  const backgroundRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const loadVanta = async () => {
      // Dynamically load Three.js and Vanta
      const script1 = document.createElement("script")
      script1.src = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
      script1.onload = () => {
        const script2 = document.createElement("script")
        script2.src = "https://cdnjs.cloudflare.com/ajax/libs/vanta.js/0.5.24/vanta.globe.min.js"
        script2.onload = () => {
          if (backgroundRef.current && (window as any).VANTA) {
            const effect = (window as any).VANTA.GLOBE({
              el: backgroundRef.current,
              color: 0x3b82f6,
              backgroundColor: 0x0a0a0a,
              size: 0.8,
            })
            return () => {
              if (effect) effect.destroy()
            }
          }
        }
        document.body.appendChild(script2)
      }
      document.body.appendChild(script1)
    }

    loadVanta()
  }, [])

  return <div ref={backgroundRef} className="fixed inset-0 -z-10 opacity-30" aria-hidden="true" />
}
