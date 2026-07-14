import { useCallback, useRef, useState } from "react"

import { uploadVideo } from "@/services/api"
import { LipReadResponse } from "@/types"

interface Props {
  onResult: (r: LipReadResponse | null) => void
  onLoading: (v: boolean) => void
  onProgress: (p: string) => void
}

export function UploadZone({ onResult, onLoading, onProgress }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = useCallback(
    async (file: File) => {
      onLoading(true)
      onProgress("Uploading...")
      onResult(null)
      try {
        const result = await uploadVideo(file)
        onResult(result)
      } catch (err) {
        onResult(null)
        onProgress(
          err instanceof Error ? err.message : "Upload failed",
        )
      } finally {
        onLoading(false)
      }
    },
    [onResult, onLoading, onProgress],
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const handleClick = () => inputRef.current?.click()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onClick={handleClick}
      className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
        dragging
          ? "border-black bg-gray-50 dark:border-white dark:bg-gray-900"
          : "border-gray-300 hover:border-gray-400 dark:border-gray-600"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".mp4,.webm"
        className="hidden"
        onChange={handleChange}
      />
      <p className="text-lg font-medium">Drop a video here</p>
      <p className="text-sm text-gray-500 mt-1">
        or click to browse (MP4, WebM — max 2 min)
      </p>
    </div>
  )
}
