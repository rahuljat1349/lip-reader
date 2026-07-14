from abc import ABC, abstractmethod

from app.domain.models import PipelineContext


class ValidationService(ABC):
    @abstractmethod
    def validate(self, ctx: PipelineContext) -> PipelineContext: ...


class VideoService(ABC):
    @abstractmethod
    def extract_frames(self, ctx: PipelineContext) -> PipelineContext: ...


class FaceDetectionService(ABC):
    @abstractmethod
    def detect(self, ctx: PipelineContext) -> PipelineContext: ...


class TrackingService(ABC):
    @abstractmethod
    def track(self, ctx: PipelineContext) -> PipelineContext: ...


class MouthExtractionService(ABC):
    @abstractmethod
    def extract(self, ctx: PipelineContext) -> PipelineContext: ...


class TensorService(ABC):
    @abstractmethod
    def create_tensor(self, ctx: PipelineContext) -> PipelineContext: ...


class InferenceService(ABC):
    @abstractmethod
    def infer(self, ctx: PipelineContext) -> PipelineContext: ...


class DecoderService(ABC):
    @abstractmethod
    def decode(self, ctx: PipelineContext) -> PipelineContext: ...
