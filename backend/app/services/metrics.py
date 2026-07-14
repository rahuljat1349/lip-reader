import time

from app.domain.models import PipelineContext


class MetricsService:
    def __init__(self):
        self._start: float | None = None

    def start(self) -> None:
        self._start = time.perf_counter()

    def record(self, ctx: PipelineContext) -> PipelineContext:
        if self._start is not None:
            ctx.metrics.processing_time = time.perf_counter() - self._start

        if ctx.frames and ctx.metrics.processing_time > 0:
            ctx.metrics.fps = len(ctx.frames) / ctx.metrics.processing_time

        return ctx
