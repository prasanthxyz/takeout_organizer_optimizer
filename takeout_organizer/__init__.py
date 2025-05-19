"""Top-level package for Takeout Organizer."""

__app_name__ = "takeout_organizer"
__description__ = "Organize your Google Takeout photos and videos"
__author__ = "Prasanth P"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    DIR_WRITE_ERROR,
    FILE_ERROR,
    FILE_WRITE_ERROR,
    JSON_ERROR,
) = range(6)

ERRORS = {
    DIR_ERROR: "directory read error",
    DIR_WRITE_ERROR: "directory write error",
    FILE_ERROR: "file read error",
    FILE_WRITE_ERROR: "file write error",
    JSON_ERROR: "json file error",
}
