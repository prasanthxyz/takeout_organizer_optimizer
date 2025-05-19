"""Takeout Organizer entry point script."""

from takeout_organizer import __app_name__, cli


def main() -> None:
    """Main entry point for the Takeout Organizer CLI."""
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    main()
