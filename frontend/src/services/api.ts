import { LipReadResponse } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function uploadVideo(file: File): Promise<LipReadResponse> {
  const formData = new FormData()
  formData.append("file", file)

  const res = await fetch(`${API_BASE}/api/v1/lipread`, {
    method: "POST",
    body: formData,
  })

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.statusText}`)
  }

  return res.json()
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`)
    return res.ok
  } catch {
    return false
  }
}
