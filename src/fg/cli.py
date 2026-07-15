from pathlib import Path
import click
from fg.core.hashing import compute_hash

@click.group()
def cli():
    """fg - file grouping CLI."""

@cli.command("gethash")
@click.argument("filepath", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def gethash(filepath: Path):
    """Compute and print the hash of a file."""
    file_hash = compute_hash(filepath)
    click.echo(f"{filepath} -> {file_hash}")

if __name__ == "__main__":
    cli()
