"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Shield } from "lucide-react"
import { cn } from "@/lib/utils"

export function Header() {
  const pathname = usePathname()

  const navItems = [
    { href: "/", label: "Dashboard" },
    { href: "/alerts", label: "Alerts" },
    { href: "/fl-status", label: "FL Status" },
    { href: "/attack-graph", label: "Attack Graph" },
  ]

  return (
    <header
      className="border-b border-slate-800 bg-slate-950 sticky top-0 z-50"
      style={{ backdropFilter: "blur(8px)" }}
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex items-center gap-3">
            <Shield size={40} className="text-blue-400" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-blue-500 to-green-400 bg-clip-text text-transparent">
              OSB Watchtower
            </h1>
          </div>

          <nav className="flex flex-col md:flex-row items-center gap-8">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "transition-colors duration-200 font-medium",
                    isActive ? "text-blue-400" : "text-gray-400 hover:text-blue-300",
                  )}
                >
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </header>
  )
}
