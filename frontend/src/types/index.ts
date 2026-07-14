export interface LipReadResponse {
  transcript: string
  confidence: number
  metrics: {
    device: string
    processingTime: number
    inferenceTime: number
  }
}

export interface ProgressUpdate {
  stage:
    | "uploading"
    | "validating"
    | "extracting_frames"
    | "detecting_face"
    | "tracking_face"
    | "extracting_mouth"
    | "running_model"
    | "decoding"
    | "completed"
    | "error"
  progress: number
  message?: string
}

export interface WebSocketMessage {
  transcript: string
  confidence: number
  progress: number
  final: boolean
}
