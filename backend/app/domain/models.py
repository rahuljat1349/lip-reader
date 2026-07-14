from dataclasses import dataclass, field

import numpy as np


@dataclass
class VideoMetadata:
    filename: str
    duration_sec: float
    fps: float
    width: int
    height: int
    codec: str


@dataclass
class FaceTrack:
    track_id: int
    bboxes: list[tuple[int, int, int, int]]
    confidence: float


@dataclass
class PipelineMetrics:
    device: str = ""
    processing_time: float = 0.0
    preprocessing_time: float = 0.0
    inference_time: float = 0.0
    fps: float = 0.0


@dataclass
class PipelineContext:
    video_path: str = ""
    metadata: VideoMetadata | None = None
    frames: list[np.ndarray] = field(default_factory=list)
    tracks: list[FaceTrack] = field(default_factory=list)
    mouth_frames: list[np.ndarray] = field(default_factory=list)
    tensor: object = None
    logits: object = None
    transcript: str = ""
    confidence: float = 0.0
    metrics: PipelineMetrics = field(default_factory=PipelineMetrics)
    errors: list[str] = field(default_factory=list)
    job_id: str = ""
    progress: str = ""
