import subprocess
import tempfile

import pytest


@pytest.fixture
def test_video_path():
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        path = f.name

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=224x224:d=1",
            "-c:v", "libx264", "-preset", "ultrafast",
            path,
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    yield path
    import os
    os.unlink(path)
