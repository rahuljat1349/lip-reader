"use client"

import { useEffect } from "react"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export function KeepAlive() {
  useEffect(() => {
    const ping = () => {
      fetch(`${BACKEND_URL}/health`).catch(() => {})
    }
    ping()
    const id = setInterval(ping, 300_000)
    return () => clearInterval(id)
  }, [])

  return null
}
