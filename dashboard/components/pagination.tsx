"use client"

import { ChevronLeft, ChevronRight } from "lucide-react"
import { Card } from "./card"

interface PaginationProps {
  currentPage: number
  totalPages: number
  totalItems: number
  itemsPerPage: number
  onPageChange: (page: number) => void
}

export function Pagination({ currentPage, totalPages, totalItems, itemsPerPage, onPageChange }: PaginationProps) {
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  const getPageNumbers = () => {
    const pages = []
    const maxPages = 5
    let start = Math.max(1, currentPage - Math.floor(maxPages / 2))
    const end = Math.min(totalPages, start + maxPages - 1)

    if (end - start + 1 < maxPages) {
      start = Math.max(1, end - maxPages + 1)
    }

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    return pages
  }

  return (
    <Card className="p-0 border-t border-gray-800 mt-6">
      <div className="px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
        <span className="text-sm text-gray-400">
          Showing {startItem} to {endItem} of {totalItems} alerts
        </span>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="p-2 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors"
            aria-label="Previous page"
          >
            <ChevronLeft size={16} />
          </button>

          {getPageNumbers().map((page) => (
            <button
              key={page}
              onClick={() => onPageChange(page)}
              className={`px-3 py-1 rounded-md transition-colors ${
                page === currentPage ? "bg-blue-500 text-white" : "hover:bg-gray-700 text-gray-400"
              }`}
            >
              {page}
            </button>
          ))}

          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="p-2 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors"
            aria-label="Next page"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </Card>
  )
}
