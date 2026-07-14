from app.domain.interfaces import TrackingService
from app.domain.models import PipelineContext


class TrackingServiceImpl(TrackingService):
    def track(self, ctx: PipelineContext) -> PipelineContext:
        ctx.progress = "tracking_face"
        return ctx
