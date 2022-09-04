"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """PatternCounter."""


if __name__ == "__main__":
    main(prog_name="patterncounter")  # pragma: no cover
