from typing import Literal

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.domain.models import PipelineContext
from app.services.decoder import DecoderServiceImpl
from app.services.face_detection import FaceDetectionServiceImpl
from app.services.inference import InferenceServiceImpl
from app.services.metrics import MetricsService
from app.services.mouth_extraction import MouthExtractionServiceImpl
from app.services.tensor_service import TensorServiceImpl
from app.services.validation import ValidationServiceImpl
from app.services.video import VideoServiceImpl


def validate_node(ctx: PipelineContext) -> PipelineContext:
    return ValidationServiceImpl().validate(ctx)


def preprocess_node(ctx: PipelineContext) -> PipelineContext:
    return VideoServiceImpl().extract_frames(ctx)


def detect_node(ctx: PipelineContext) -> PipelineContext:
    return FaceDetectionServiceImpl().detect(ctx)


def extract_mouth_node(ctx: PipelineContext) -> PipelineContext:
    return MouthExtractionServiceImpl().extract(ctx)


def tensorize_node(ctx: PipelineContext) -> PipelineContext:
    return TensorServiceImpl().create_tensor(ctx)


def infer_node(ctx: PipelineContext) -> PipelineContext:
    return InferenceServiceImpl().infer(ctx)


def decode_node(ctx: PipelineContext) -> PipelineContext:
    return DecoderServiceImpl().decode(ctx)


_metrics = MetricsService()


def metrics_start_node(ctx: PipelineContext) -> PipelineContext:
    _metrics.start()
    return ctx


def metrics_end_node(ctx: PipelineContext) -> PipelineContext:
    return _metrics.record(ctx)


def error_node(ctx: PipelineContext) -> PipelineContext:
    ctx.progress = "error"
    return ctx


def route_after_validate(
    ctx: PipelineContext,
) -> Literal["preprocess", "error"]:
    if ctx.errors:
        return "error"
    return "preprocess"


def route_after_preprocess(
    ctx: PipelineContext,
) -> Literal["detect", "error"]:
    if ctx.errors:
        return "error"
    return "detect"


def route_after_detect(
    ctx: PipelineContext,
) -> Literal["extract_mouth", "error"]:
    if ctx.errors:
        return "error"
    return "extract_mouth"


def route_after_mouth(
    ctx: PipelineContext,
) -> Literal["tensorize", "error"]:
    if ctx.errors:
        return "error"
    return "tensorize"


def route_after_tensor(
    ctx: PipelineContext,
) -> Literal["infer", "error"]:
    if ctx.errors:
        return "error"
    return "infer"


def route_after_infer(
    ctx: PipelineContext,
) -> Literal["decode", "error"]:
    if ctx.errors:
        return "error"
    return "decode"


def build_graph() -> CompiledStateGraph:
    workflow = StateGraph(PipelineContext)

    workflow.add_node("metrics_start", metrics_start_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("preprocess", preprocess_node)
    workflow.add_node("detect", detect_node)
    workflow.add_node("extract_mouth", extract_mouth_node)
    workflow.add_node("tensorize", tensorize_node)
    workflow.add_node("infer", infer_node)
    workflow.add_node("decode", decode_node)
    workflow.add_node("metrics_end", metrics_end_node)
    workflow.add_node("error", error_node)

    workflow.set_entry_point("metrics_start")

    workflow.add_edge("metrics_start", "validate")

    workflow.add_conditional_edges(
        "validate", route_after_validate, {"preprocess": "preprocess", "error": "error"}
    )
    workflow.add_conditional_edges(
        "preprocess", route_after_preprocess, {"detect": "detect", "error": "error"}
    )
    workflow.add_conditional_edges(
        "detect",
        route_after_detect,
        {"extract_mouth": "extract_mouth", "error": "error"},
    )
    workflow.add_conditional_edges(
        "extract_mouth",
        route_after_mouth,
        {"tensorize": "tensorize", "error": "error"},
    )
    workflow.add_conditional_edges(
        "tensorize", route_after_tensor, {"infer": "infer", "error": "error"}
    )
    workflow.add_conditional_edges(
        "infer", route_after_infer, {"decode": "decode", "error": "error"}
    )

    workflow.add_edge("decode", "metrics_end")
    workflow.add_edge("metrics_end", END)
    workflow.add_edge("error", END)

    return workflow.compile()
