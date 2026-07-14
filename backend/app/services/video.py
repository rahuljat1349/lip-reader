import os
import subprocess

import cv2
import numpy as np

from app.config import settings
from app.domain.interfaces import VideoService
from app.domain.models import PipelineContext


class VideoServiceImpl(VideoService):
    def extract_frames(self, ctx: PipelineContext) -> PipelineContext:
        ctx.progress = "extracting_frames"

        fps = settings.target_fps
        target_size = settings.target_size
        job_dir = os.path.dirname(ctx.video_path)
        frames_dir = os.path.join(job_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        pattern = os.path.join(frames_dir, "frame_%06d.jpg")

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i", ctx.video_path,
                    "-vf", f"fps={fps},scale={target_size[0]}:{target_size[1]},format=rgb24",
                    "-qscale:v", "2",
                    "-y",
                    pattern,
                ],
                capture_output=True,
                text=True,
                timeout=300,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            ctx.errors.append(f"FFmpeg extraction failed: {e.stderr[:200]}")
            return ctx

        frame_files = sorted(
            os.path.join(frames_dir, f)
            for f in os.listdir(frames_dir)
            if f.endswith(".jpg")
        )

        frames = []
        for f in frame_files:
            img = cv2.imread(f, cv2.IMREAD_COLOR)
            if img is not None:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                frames.append(img_rgb)

        ctx.frames = frames
        return ctx
