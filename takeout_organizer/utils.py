"""Common utils"""

from pathlib import Path


def get_image_paths(directory: Path) -> list[Path]:
    """Get all image paths from the given directory and its subdirectories."""
    image_paths = []
    for path in directory.rglob("*"):
        if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".tiff"):
            image_paths.append(path)
    return sorted(image_paths)


def get_video_paths(directory: Path) -> list[Path]:
    """Get all video paths from the given directory and its subdirectories."""
    video_paths = []
    for path in directory.rglob("*"):
        if path.suffix.lower() in (".mp4", ".mov", ".avi", ".mkv", ".3gp"):
            video_paths.append(path)
    return sorted(video_paths)
