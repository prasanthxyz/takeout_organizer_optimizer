"""Organize photos and videos from Google Takeout into a structured format."""

import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional, Union

import piexif  # type: ignore[import-untyped]
from PIL import Image
from PIL.ExifTags import TAGS

from takeout_organizer.utils import get_image_paths, get_video_paths


def organize_photos_and_videos(
    input_dir: Path,
    output_dir: Path,
    delete_original_files: bool,
) -> None:
    """Organize photos and videos from the input directory to the output directory."""
    _organize_photos(
        input_dir=input_dir,
        output_dir=output_dir,
        delete_original_files=delete_original_files,
    )

    _organize_videos(
        input_dir=input_dir,
        output_dir=output_dir,
        delete_original_files=delete_original_files,
    )


def _organize_photos(
    input_dir: Path,
    output_dir: Path,
    delete_original_files: bool,
) -> None:
    """Organize photos from the input directory to the output directory."""
    for image_path in get_image_paths(input_dir):
        json_data = None
        json_path = _get_json_path(image_path)
        if json_path and json_path.exists():
            with open(json_path, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)
        if json_data is not None:
            _add_exif_to_image_file_from_json_data(image_path, json_data)

        exif_date = _get_exif_date_from_image(image_path)
        if exif_date == "":
            exif_date = "1900:01:01 00:00:00"

        # copy the image to the output directory
        filename_date = exif_date.replace(":", "-").replace(" ", "_")
        output_filename = filename_date + "-" + image_path.name
        shutil.copy2(str(image_path), str(output_dir / output_filename))

        if delete_original_files:
            image_path.unlink(missing_ok=True)
            if json_path and json_path.exists():
                json_path.unlink()


def _organize_videos(
    input_dir: Path,
    output_dir: Path,
    delete_original_files: bool,
) -> None:
    """Organize videos from the input directory to the output directory."""
    for video_path in get_video_paths(input_dir):
        json_data = None
        json_path = _get_json_path(video_path)
        if json_path and json_path.exists():
            with open(json_path, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)
        if json_data:
            video_path_with_exif = _add_exif_to_video_file_from_json_data(video_path, json_data)
        else:
            video_path_with_exif = video_path

        exif_date = _get_exif_date_from_video(video_path_with_exif)
        if exif_date == "":
            exif_date = "1900-01-01T00:00:00.000000Z"

        # Copy the video to the output directory
        filename_date = exif_date.replace(":", "-").replace("T", "_")[:19]
        output_filename = filename_date + "-" + video_path_with_exif.name
        output_path = output_dir / output_filename
        shutil.copy2(str(video_path_with_exif), str(output_path))
        if video_path != video_path_with_exif:
            video_path_with_exif.unlink(missing_ok=True)

        # Update timestamp from the filename
        timestamp = datetime.strptime(exif_date[:19], "%Y-%m-%dT%H:%M:%S")
        os.utime(output_path, (timestamp.timestamp(), timestamp.timestamp()))

        if delete_original_files:
            if video_path.exists():
                video_path.unlink()
            if json_path and json_path.exists():
                json_path.unlink()


def _get_json_path(image_path: Path) -> Optional[Path]:
    """Get the JSON path for the image's supplemental metadata file."""
    json_name = image_path.name + ".supplemental-metadata"
    json_path = image_path.with_name(json_name[:46] + ".json")
    if json_path.exists():
        return json_path
    return None


def _get_exif_date_from_image(image_path: Path) -> str:
    """Get the EXIF date from the image file."""
    image = Image.open(image_path)
    exif_data = image.getexif()

    if not exif_data:
        return ""

    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "DateTime":
            return str(value)

    return ""


def _get_exif_date_from_video(video_path: Path) -> str:
    """Get the EXIF date from the video file using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format_tags=creation_time",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error getting EXIF date for {video_path}: {e.stderr.decode()}")
        return ""
    return result.stdout.decode().strip()


def _add_exif_to_image_file_from_json_data(image_path: Path, json_data: dict[Any, Any]) -> None:
    """Add EXIF data to the image file from the JSON data."""
    exif_date = str(_get_exif_date_from_json_data(json_data))
    if not exif_date:
        print(f"EXIF date not found in JSON for {image_path}")
        return

    im = Image.open(image_path)

    exif_data = im.info.get("exif", None)
    exif_dict = {}
    if exif_data:
        try:
            exif_dict = piexif.load(exif_data)
        except Exception as e:  # pylint: disable=W0703
            print(f"Error loading EXIF data for {image_path}: {e}")

    if not exif_dict:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}

    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_date.encode()
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = exif_date.encode()
    exif_dict["0th"][piexif.ImageIFD.DateTime] = exif_date.encode()

    title = json_data.get("title")
    if title:
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = title.encode()

    gps = json_data.get("geoData", {})
    lat, lon = gps.get("latitude"), gps.get("longitude")
    if lat and lon and (lat != 0.0 or lon != 0.0):

        def to_deg(value: int) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
            """Convert decimal degrees to degrees, minutes, seconds."""
            deg = int(value)
            _min = int((value - deg) * 60)
            sec = int((value - deg - _min / 60) * 3600 * 100)
            return ((deg, 1), (_min, 1), (sec, 100))

        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: b"N" if lat >= 0 else b"S",
            piexif.GPSIFD.GPSLatitude: to_deg(abs(lat)),
            piexif.GPSIFD.GPSLongitudeRef: b"E" if lon >= 0 else b"W",
            piexif.GPSIFD.GPSLongitude: to_deg(abs(lon)),
        }
        exif_dict["GPS"] = gps_ifd

    try:
        exif_bytes = piexif.dump(exif_dict)
    except Exception as e:  # pylint: disable=W0703
        print(f"Error dumping EXIF data for {image_path}: {e}")
        return

    im.save(image_path, exif=exif_bytes)


def _add_exif_to_video_file_from_json_data(video_path: Path, json_data: dict[Any, Any]) -> Path:
    """Add EXIF data to the video file from the JSON data."""
    exif_date = _get_exif_date_from_json_data(json_data, get_dt_obj=True)
    if not exif_date:
        print(f"EXIF date not found in JSON for {video_path}")
        return video_path
    if not isinstance(exif_date, datetime):
        print(f"EXIF date is not a datetime object for {video_path}")
        return video_path

    temp_path = video_path.with_name(video_path.stem + "_temp.mp4")

    if video_path.suffix.lower() == ".mp4":
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-map_metadata",
            "0",
            "-metadata",
            f"creation_time={exif_date.isoformat()}Z",
            "-movflags",
            "use_metadata_tags",
            "-c",
            "copy",
            str(temp_path),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        temp_path.replace(video_path)
        return video_path

    # The file wasn't .mp4, so we need to convert it
    cmd = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-map_metadata",
        "0",
        "-metadata",
        f"creation_time={exif_date.isoformat()}Z",
        "-movflags",
        "use_metadata_tags",
        str(temp_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    video_path = video_path.with_suffix(".mp4")
    temp_path.replace(video_path)
    return video_path


def _get_exif_date_from_json_data(json_data: dict[Any, Any], get_dt_obj: bool = False) -> Union[str, datetime]:
    """Get the EXIF date from the JSON data."""
    timestamp_str = json_data.get("photoTakenTime", {}).get("timestamp")
    if not timestamp_str:
        return ""

    timestamp = int(timestamp_str)
    dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    # TODO: Handle timezone conversion based on user input instead of defaulting to IST pylint: disable=W0511
    dt_ist = dt_utc.astimezone(timezone(timedelta(hours=5, minutes=30)))

    if get_dt_obj:
        return dt_ist

    exif_datetime = dt_ist.strftime("%Y:%m:%d %H:%M:%S")
    return exif_datetime
