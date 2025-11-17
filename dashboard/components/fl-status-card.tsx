import { Card } from "./card"
import { ProgressBar } from "./progress-bar"
import { FacilityStatus } from "./facility-status"

interface Facility {
  name: string
  status: "active" | "delayed"
}

interface FLStatusCardProps {
  roundNumber: number
  progress: number
  facilities: Facility[]
  epsilon: number
  delta: string
}

export function FLStatusCard({ roundNumber, progress, facilities, epsilon, delta }: FLStatusCardProps) {
  const hasActiveRound = roundNumber > 0

  return (
    <Card>
      <h2 className="text-xl font-semibold mb-6 text-white">Federated Learning</h2>

      {!hasActiveRound ? (
        <div className="text-center py-8">
          <p className="text-gray-400">No active round</p>
        </div>
      ) : (
        <div className="space-y-6">
          <div>
            <p className="text-sm text-gray-400 mb-2">Round #{roundNumber}</p>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-400">Training Progress</span>
              <span className="text-sm font-mono text-blue-400">{progress}%</span>
            </div>
            <ProgressBar percentage={progress} />
          </div>

          {facilities.length > 0 && (
            <div>
              <p className="text-sm text-gray-400 mb-3">Facility Status</p>
              <div className="grid grid-cols-3 gap-4">
                {facilities.map((facility) => (
                  <FacilityStatus key={facility.name} name={facility.name} status={facility.status} />
                ))}
              </div>
            </div>
          )}

          <div className="pt-4 border-t border-slate-700 space-y-2">
            <p className="text-xs text-gray-400">
              Privacy Budget: ε = {epsilon}, δ = {delta}
            </p>
          </div>
        </div>
      )}
    </Card>
  )
}
