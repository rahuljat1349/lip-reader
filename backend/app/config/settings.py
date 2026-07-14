from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "LipReader"
    debug: bool = True
    upload_dir: str = "uploads"
    max_video_duration: int = 120
    max_file_size_mb: int = 100
    allowed_formats: list[str] = ["mp4", "webm"]
    target_fps: int = 25
    target_size: tuple[int, int] = (224, 224)
    model_name: str = "av-hubert"
    device: str = "auto"
    ws_max_frames: int = 300
    temp_dir: str = "tmp"
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_prefix": "LIPREADER_", "env_file": ".env"}


settings = Settings()
