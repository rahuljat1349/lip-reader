import os
import subprocess
import json

from app.config import settings
from app.domain.interfaces import ValidationService
from app.domain.models import PipelineContext, VideoMetadata


class ValidationServiceImpl(ValidationService):
    def validate(self, ctx: PipelineContext) -> PipelineContext:
        ctx.progress = "validating"

        path = ctx.video_path
        if not path:
            ctx.errors.append("No file provided")
            return ctx

        ext = os.path.splitext(path)[1].lstrip(".").lower()
        if ext not in settings.allowed_formats:
            ctx.errors.append(
                f"Unsupported format '{ext}'. Allowed: {settings.allowed_formats}"
            )
            return ctx

        if not os.path.isfile(path):
            ctx.errors.append("File not found")
            return ctx

        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            ctx.errors.append(
                f"File too large ({size_mb:.1f} MB). Max: {settings.max_file_size_mb} MB"
            )
            return ctx

        metadata = self._get_metadata(path)
        if metadata is None:
            ctx.errors.append("Could not read video metadata")
            return ctx

        if metadata.duration_sec > settings.max_video_duration:
            ctx.errors.append(
                f"Video too long ({metadata.duration_sec:.0f}s). Max: {settings.max_video_duration}s"
            )
            return ctx

        ctx.metadata = metadata
        return ctx

    @staticmethod
    def _get_metadata(path: str) -> VideoMetadata | None:
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    path,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            data = json.loads(result.stdout)
            stream = next(
                (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
                None,
            )
            if not stream:
                return None

            fmt = data.get("format", {})
            duration = float(fmt.get("duration", 0))
            fps_parts = stream.get("r_frame_rate", "0/1").split("/")
            fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 0

            return VideoMetadata(
                filename=os.path.basename(path),
                duration_sec=duration,
                fps=fps,
                width=int(stream.get("width", 0)),
                height=int(stream.get("height", 0)),
                codec=stream.get("codec_name", ""),
            )
        except Exception:
            return None
