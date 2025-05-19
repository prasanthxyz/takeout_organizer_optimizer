"""This module provides the Takeout Organizer CLI."""

from pathlib import Path
from typing import Optional

import typer

from takeout_organizer import DIR_ERROR, DIR_WRITE_ERROR, __app_name__, __version__
from takeout_organizer.optimizer_utils import optimize_photos
from takeout_organizer.organizer_utils import organize_photos_and_videos

app = typer.Typer()


def _version_callback(value: bool) -> None:
    """Display the version of the application and exit."""
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    """Main callback function for the Takeout Organizer CLI."""
    return


@app.command()
def organize(
    input_dir: str = typer.Option(..., help="Path to the input directory."),
    output_dir: str = typer.Option(..., help="Path to the output directory."),
    delete_original_files: bool = typer.Option(False, help="Delete original files after organizing."),
) -> None:
    """Organize Google Takeout and other photos and videos."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        typer.echo(f"Input directory '{input_path}' does not exist.")
        raise typer.Exit(DIR_ERROR)

    if not output_path.exists():
        typer.echo(f"Output directory '{output_path}' does not exist, trying to create it.")
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            typer.echo(f"Failed to create output directory '{output_path}': {e}")
            raise typer.Exit(DIR_WRITE_ERROR)

    if input_path == output_path:
        typer.echo("Input and output directories cannot be the same.")
        raise typer.Exit(DIR_ERROR)

    organize_photos_and_videos(input_path, output_path, delete_original_files)


@app.command()
def optimize(
    input_dir: str = typer.Option(..., help="Path to the input directory."),
    output_dir: str = typer.Option(..., help="Path to the output directory."),
    max_width: int = typer.Option(2000, help="Maximum width of the photos."),
    max_height: int = typer.Option(2000, help="Maximum height of the photos."),
    delete_original_files: bool = typer.Option(False, help="Delete original files after optimizing."),
) -> None:
    """Optimize a photos and videos collection."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        typer.echo(f"Input directory '{input_path}' does not exist.")
        raise typer.Exit(DIR_ERROR)

    if not output_path.exists():
        typer.echo(f"Output directory '{output_path}' does not exist, trying to create it.")
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            typer.echo(f"Failed to create output directory '{output_path}': {e}")
            raise typer.Exit(DIR_WRITE_ERROR)

    if input_path == output_path:
        typer.echo("Input and output directories cannot be the same.")
        raise typer.Exit(DIR_ERROR)

    optimize_photos(input_path, output_path, max_width, max_height, delete_original_files)
