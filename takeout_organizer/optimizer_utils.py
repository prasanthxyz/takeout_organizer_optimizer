"""Organize photos and videos from Google Takeout into a structured format."""

from pathlib import Path

from PIL import Image

from takeout_organizer.utils import get_image_paths


def optimize_photos(
    input_dir: Path,
    output_dir: Path,
    max_width: int,
    max_height: int,
    delete_original_files: bool,
) -> None:
    """Optimize photos and videos from the input directory to the output directory."""
    for image_path in get_image_paths(input_dir):
        # mogrify -resize '2000x2000>' -path output_dir image_path
        with Image.open(image_path) as img:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            output_path = output_dir / image_path.name
            img.save(output_path, quality=100)

        if delete_original_files:
            image_path.unlink(missing_ok=True)
