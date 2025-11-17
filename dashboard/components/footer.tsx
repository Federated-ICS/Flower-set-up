import { Github, Settings, HelpCircle } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-gray-800 bg-slate-950 mt-12" style={{ backdropFilter: "blur(8px)" }}>
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-gray-400 text-sm">
            © 2025 OSB Watchtower<span className="ml-3 text-xs">v1.0.0</span>
          </div>

          <div className="flex items-center gap-6">
            <button className="text-gray-400 hover:text-blue-400 transition-colors duration-200" aria-label="GitHub">
              <Github size={20} />
            </button>
            <button className="text-gray-400 hover:text-blue-400 transition-colors duration-200" aria-label="Settings">
              <Settings size={20} />
            </button>
            <button className="text-gray-400 hover:text-blue-400 transition-colors duration-200" aria-label="Help">
              <HelpCircle size={20} />
            </button>
          </div>
        </div>
      </div>
    </footer>
  )
}
