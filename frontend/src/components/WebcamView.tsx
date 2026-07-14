"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision"

import { connectWebSocket } from "@/services/websocket"
import { LipReadResponse, WebSocketMessage } from "@/types"

interface Props {
  onResult: (r: LipReadResponse | null) => void
  onLoading: (v: boolean) => void
  onProgress: (p: string) => void
}

const SPEAKING_THRESHOLD = 0.05
const LIP_TOP = 13
const LIP_BOTTOM = 14
const LIP_LEFT = 61
const LIP_RIGHT = 291

function lipDistance(landmarks: number[][]): number {
  const top = landmarks[LIP_TOP]
  const bottom = landmarks[LIP_BOTTOM]
  const left = landmarks[LIP_LEFT]
  const right = landmarks[LIP_RIGHT]
  if (!top || !bottom || !left || !right) return 0
  const v = Math.hypot(top[0] - bottom[0], top[1] - bottom[1])
  const h = Math.hypot(left[0] - right[0], left[1] - right[1])
  return h === 0 ? 0 : v / h
}

function drawFaceMesh(
  ctx: CanvasRenderingContext2D,
  landmarks: number[][],
  speaking: boolean,
) {
  const w = ctx.canvas.width
  const h = ctx.canvas.height

  ctx.strokeStyle = speaking ? "#22c55e" : "#ef4444"
  ctx.lineWidth = 1.5

  const connections = [
    [61, 146], [146, 91], [91, 181], [181, 84], [84, 17],
    [17, 314], [314, 405], [405, 321], [321, 375], [375, 291],
    [61, 185], [185, 40], [40, 39], [39, 37], [37, 0],
    [0, 267], [267, 269], [269, 270], [270, 409], [409, 291],
    [78, 191], [191, 80], [80, 81], [81, 82], [82, 13],
    [13, 312], [312, 311], [311, 310], [310, 415], [415, 308],
    [308, 324], [324, 318], [318, 402], [402, 317], [317, 14],
    [14, 87], [87, 178], [178, 88], [88, 95],
  ]

  for (const [i, j] of connections) {
    const p = landmarks[i]
    const q = landmarks[j]
    if (!p || !q) continue
    ctx.beginPath()
    ctx.moveTo(p[0] * w, p[1] * h)
    ctx.lineTo(q[0] * w, q[1] * h)
    ctx.stroke()
  }
}

export function WebcamView({ onResult, onLoading, onProgress }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const animRef = useRef<number>(0)
  const [streaming, setStreaming] = useState(false)
  const [landmarkerReady, setLandmarkerReady] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const [liveTranscript, setLiveTranscript] = useState("")
  const [liveConfidence, setLiveConfidence] = useState(0)
  const landmarkerRef = useRef<FaceLandmarker | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const sendQueueRef = useRef<number[]>([])
  const lastSendRef = useRef(0)

  useEffect(() => {
    const load = async () => {
      const fileset = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm",
      )
      landmarkerRef.current = await FaceLandmarker.createFromOptions(
        fileset,
        {
          baseOptions: {
            modelAssetPath: "/face_landmarker.task",
            delegate: "GPU",
          },
          runningMode: "VIDEO",
          numFaces: 1,
          outputFaceBlendshapes: false,
          outputFacialTransformationMatrixes: false,
        },
      )
      setLandmarkerReady(true)
    }
    load()
  }, [])

  const processFrame = useCallback(() => {
    const video = videoRef.current
    const canvas = canvasRef.current
    const landmarker = landmarkerRef.current
    if (!video || !canvas || !landmarker || video.readyState < 2) {
      animRef.current = requestAnimationFrame(processFrame)
      return
    }

    const cctx = canvas.getContext("2d")!
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    cctx.clearRect(0, 0, canvas.width, canvas.height)

    const result = landmarker.detectForVideo(video, performance.now())

    if (result.faceLandmarks && result.faceLandmarks.length > 0) {
      const landmarks = result.faceLandmarks[0]
      const pts = landmarks.map((lm) => [lm.x, lm.y])

      const mar = lipDistance(pts)
      const isSpeaking = mar > SPEAKING_THRESHOLD
      setSpeaking(isSpeaking)

      drawFaceMesh(cctx, pts, isSpeaking)

      if (isSpeaking) {
        const now = Date.now()
        sendQueueRef.current.push(now)
        sendQueueRef.current = sendQueueRef.current.filter(
          (t) => now - t < 3000,
        )

        if (
          wsRef.current?.readyState === WebSocket.OPEN &&
          now - lastSendRef.current > 200
        ) {
          lastSendRef.current = now
          const offscreen = new OffscreenCanvas(
            video.videoWidth,
            video.videoHeight,
          )
          const octx = offscreen.getContext("2d")!
          octx.drawImage(video, 0, 0)
          offscreen.convertToBlob({ type: "image/jpeg", quality: 0.7 }).then(
            (blob) => {
              if (wsRef.current?.readyState === WebSocket.OPEN) {
                blob.arrayBuffer().then((buf) => {
                  wsRef.current?.send(buf)
                })
              }
            },
          )
        }
      }
    }

    animRef.current = requestAnimationFrame(processFrame)
  }, [])

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
      setStreaming(true)

      onProgress("Connecting...")

      const ws = connectWebSocket(
        (msg: WebSocketMessage) => {
          setLiveTranscript(msg.transcript)
          setLiveConfidence(msg.confidence)
          if (msg.final) {
            onResult({
              transcript: msg.transcript,
              confidence: msg.confidence,
              metrics: {
                device: "",
                processingTime: 0,
                inferenceTime: 0,
              },
            })
            onLoading(false)
          }
        },
        () => onLoading(false),
        () => {
          setStreaming(false)
          onLoading(false)
        },
        () => {
          onLoading(false)
          onProgress("")
        },
      )
      wsRef.current = ws

      videoRef.current!.play()
      animRef.current = requestAnimationFrame(processFrame)
    } catch {
      onProgress("Camera access denied")
      onLoading(false)
    }
  }

  const stopWebcam = () => {
    cancelAnimationFrame(animRef.current)
    wsRef.current?.close()
    wsRef.current = null
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    setStreaming(false)
    setSpeaking(false)
    setLiveTranscript("")
  }

  useEffect(() => {
    return () => {
      stopWebcam()
    }
  }, [])

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-full max-w-md">
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className="rounded-xl w-full bg-black"
        />
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full pointer-events-none"
        />
      </div>

      <div className="flex items-center gap-6">
        {!streaming ? (
          <button
            onClick={startWebcam}
            disabled={!landmarkerReady}
            className="px-6 py-2 bg-black text-white rounded-lg font-medium hover:opacity-80 transition-opacity disabled:opacity-50 dark:bg-white dark:text-black"
          >
            {landmarkerReady ? "Start Webcam" : "Loading model..."}
          </button>
        ) : (
          <button
            onClick={stopWebcam}
            className="px-6 py-2 bg-red-600 text-white rounded-lg font-medium hover:opacity-80 transition-opacity"
          >
            Stop
          </button>
        )}

        {streaming && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span
                className={`w-3 h-3 rounded-full ${
                  speaking ? "bg-green-500" : "bg-red-500"
                }`}
              />
              <span className="text-sm font-medium">
                {speaking ? "Speaking" : "Not Speaking"}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Confidence:{" "}
              <span className="font-semibold">
                {Math.round(liveConfidence * 100)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {liveTranscript && (
        <div className="text-center space-y-1">
          <p className="text-lg italic text-gray-600 dark:text-gray-400">
            {liveTranscript}
          </p>
          {liveConfidence > 0 && (
            <p className="text-xs text-gray-400">
              confidence: {String(Math.round(liveConfidence * 100))}%
            </p>
          )}
        </div>
      )}

      {!landmarkerReady && (
        <p className="text-sm text-gray-500">Loading face landmark model...</p>
      )}
    </div>
  )
}
