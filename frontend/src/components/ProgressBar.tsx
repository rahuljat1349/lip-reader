const STAGES = [
  "uploading",
  "validating",
  "extracting_frames",
  "detecting_face",
  "tracking_face",
  "extracting_mouth",
  "running_model",
  "decoding",
  "completed",
] as const

const LABELS: Record<string, string> = {
  uploading: "Uploading",
  validating: "Validating",
  extracting_frames: "Extracting frames",
  detecting_face: "Detecting face",
  tracking_face: "Tracking face",
  extracting_mouth: "Extracting mouth",
  running_model: "Running model",
  decoding: "Decoding",
  completed: "Completed",
}

interface Props {
  current: string
}

export function ProgressBar({ current }: Props) {
  const idx = STAGES.indexOf(current as typeof STAGES[number])
  if (idx === -1) return null

  const progress = ((idx + 1) / STAGES.length) * 100

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between text-sm text-gray-500">
        <span>{LABELS[current] || current}</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
        <div
          className="bg-black dark:bg-white h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}
