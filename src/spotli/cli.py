import sys
import click

from .base.authorization import auth
from .player.commands import player

from dotenv import load_dotenv

load_dotenv()


@click.group()
@click.option("--debug", is_flag=True, help="Display full error traceback")
def cli(debug):
    """Simple python cli tool to manage your Spotify sessions from within the terminal.

    As this tool performs all operation via Spotify API, you need constant
    internet access and active Spotify session on any device with your
    account connected.

    Before you start, authenticate yourself with `spotli auth`.

    For detailed traceback put --debug right after `spotli` command.
    """
    if not debug:
        sys.tracebacklimit = 0


cli.add_command(auth)
cli.add_command(player)

if __name__ == "__main__":
    cli()
