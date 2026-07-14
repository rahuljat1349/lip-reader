import { LipReadResponse } from "@/types"

interface Props {
  result: LipReadResponse
}

export function TranscriptView({ result }: Props) {
  return (
    <div className="w-full max-w-xl bg-gray-50 dark:bg-gray-900 rounded-xl p-6 space-y-4">
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          Transcript
        </h2>
        <p className="text-xl mt-1">{result.transcript || "(no speech detected)"}</p>
      </div>

      <div className="flex gap-6">
        <div>
          <span className="text-sm text-gray-500">Confidence</span>
          <p className="text-lg font-semibold">
            {(result.confidence * 100).toFixed(1)}%
          </p>
        </div>
        <div>
          <span className="text-sm text-gray-500">Device</span>
          <p className="text-lg font-semibold">{result.metrics.device || "—"}</p>
        </div>
        <div>
          <span className="text-sm text-gray-500">Processing</span>
          <p className="text-lg font-semibold">
            {result.metrics.processingTime.toFixed(1)}s
          </p>
        </div>
      </div>
    </div>
  )
}
