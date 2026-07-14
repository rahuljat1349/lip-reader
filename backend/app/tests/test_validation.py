from app.domain.models import PipelineContext
from app.services.validation import ValidationServiceImpl


def test_validate_missing_file_returns_error():
    ctx = PipelineContext(video_path="/nonexistent/video.mp4")
    service = ValidationServiceImpl()
    result = service.validate(ctx)
    assert any("File not found" in e for e in result.errors)


def test_validate_unsupported_format_returns_error():
    ctx = PipelineContext(video_path="video.avi")
    service = ValidationServiceImpl()
    result = service.validate(ctx)
    assert any("Unsupported format" in e for e in result.errors)


def test_validate_sets_metadata_for_valid_video(test_video_path):
    ctx = PipelineContext(video_path=test_video_path)
    service = ValidationServiceImpl()
    result = service.validate(ctx)
    assert not result.errors
    assert result.metadata is not None
    assert result.metadata.duration_sec > 0
