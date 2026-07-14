import { WebSocketMessage } from "@/types"

const WS_BASE =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/live"

export function connectWebSocket(
  onMessage: (msg: WebSocketMessage) => void,
  onError?: (err: Event) => void,
  onClose?: () => void,
  onOpen?: () => void,
): WebSocket {
  const ws = new WebSocket(WS_BASE)

  ws.onopen = () => {
    console.log("WebSocket connected")
    onOpen?.()
  }

  ws.onmessage = (event) => {
    const msg: WebSocketMessage = JSON.parse(event.data)
    onMessage(msg)
  }

  ws.onerror = (err) => {
    console.error("WebSocket error:", err)
    onError?.(err)
  }

  ws.onclose = () => {
    console.log("WebSocket closed")
    onClose?.()
  }

  return ws
}
