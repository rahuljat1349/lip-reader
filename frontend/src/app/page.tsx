"use client"

import { useState } from "react"

import { UploadZone } from "@/components/UploadZone"
import { WebcamView } from "@/components/WebcamView"
import { TranscriptView } from "@/components/TranscriptView"
import { LipReadResponse } from "@/types"

type Mode = "upload" | "webcam"

export default function Home() {
  const [mode, setMode] = useState<Mode>("upload")
  const [result, setResult] = useState<LipReadResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState<string>("")

  return (
    <main className="flex-1 flex flex-col items-center justify-center p-8 gap-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">LipReader</h1>
        <p className="text-gray-500 mt-2">
          Convert lip movements into text
        </p>
      </header>

      <div className="flex gap-4">
        <button
          onClick={() => setMode("upload")}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            mode === "upload"
              ? "bg-black text-white dark:bg-white dark:text-black"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300"
          }`}
        >
          Upload Video
        </button>
        <button
          onClick={() => setMode("webcam")}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            mode === "webcam"
              ? "bg-black text-white dark:bg-white dark:text-black"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300"
          }`}
        >
          Live Webcam
        </button>
      </div>

      <div className="w-full max-w-xl">
        {mode === "upload" ? (
          <UploadZone
            onResult={setResult}
            onLoading={setLoading}
            onProgress={setProgress}
          />
        ) : (
          <WebcamView
            onResult={setResult}
            onLoading={setLoading}
            onProgress={setProgress}
          />
        )}
      </div>

      {loading && progress && (
        <p className="text-sm text-gray-500">{progress}</p>
      )}

      {result && <TranscriptView result={result} />}
    </main>
  )
}
