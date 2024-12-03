import sys

import click
from dotenv import load_dotenv

from .authorization import SpotifyAuth
from .commons import SpotifyURI
from .exceptions import MissingRequiredArgumentsError
from .player import Player

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


@cli.command(context_settings={"auto_envvar_prefix": "SPOTLI"})
@click.option("--redirect_uri", help="Overwrites SPOTLI_REDIRECT_URI", type=str)
@click.option("--client_secret", help="Overwrites SPOTLI_CLIENT_SECRET", type=str)
@click.option("--client_id", help="Overwrites SPOTLI_CLIENT_ID", type=str)
def auth(client_id, client_secret, redirect_uri):
    """Authenticate user using oAuth and create access token\n
    prerequisition: Spotify App\n
    (see: https://developer.spotify.com/documentation/web-api/concepts/apps)

    You can pass your credentials to the the command directly or more convieniently
    store them in environment variables
    """
    try:
        SpotifyAuth(client_id, client_secret, redirect_uri).get_access_token()
    except KeyboardInterrupt:
        raise click.Abort()
    except MissingRequiredArgumentsError as err:
        click.echo("Missing required user credentials")
        for cred in err.missing_args:
            click.secho(f" - {cred}", fg="red")
    except Exception as err:
        raise err


@click.group(invoke_without_command=True)
@click.pass_context
def player(ctx):
    """Manage Spotify's web player

    By default displays status of the current player.
    """
    if not ctx.invoked_subcommand:
        ctx.invoke(status)


@player.command()
@click.option("--short", is_flag=True, help="If set, displayes status in short form")
def status(short):
    """Displays status of the current active Device"""
    player = Player()

    result = player.status() if not short else player.status_short()

    click.echo(result)


@player.command()
def play():
    """Starts playback; Targets current active session"""
    player = Player()

    result = player.play()

    click.echo(result)


@player.command()
def pause():
    """Pause playback; Targets current active session"""
    player = Player()

    result = player.pause()

    click.echo(result)


@player.command(context_settings={"ignore_unknown_options": True})
@click.argument("value", type=int, nargs=1)
def volume(value):
    """Change volume of current active session to <VALUE>"""

    player = Player()

    result = player.volume(value)

    click.echo(result)


@player.command()
def next():
    """Skips to next track in the user's queue"""

    player = Player()

    result = player.next()

    click.echo(result)


@player.command()
def previous():
    """Skips to previous track in the user's queue"""

    player = Player()

    result = player.previous()

    click.echo(result)


@player.command()
@click.argument("value", type=click.DateTime(formats=["%H:%M:%S", "%M:%S"]), nargs=1)
def seek(value):
    """Seek to the given <VALUE> in the currently playing track; Format 00:00:00 or 00:00."""

    player = Player()

    result = player.seek(value)

    click.echo(result)


@player.command()
@click.argument(
    "value",
    type=click.Choice(["track", "context", "off"], case_sensitive=False),
    nargs=1,
)
def repeat(value):
    """Set player to repeat mode\n
    `track` - repeat current track\n
    `context` - repeat current context (album, queue)\n
    `off` - turns off repeat mode
    """

    player = Player()

    result = player.repeat(value)

    click.echo(result)


@player.command()
def devices():
    """Returns list of available Spotify Connect devices\n
    🟢 active     | inactive     🔴\n
    🙈 private    | unprivate    🐵\n
    🔐 restricted | unrestricted 🔓
    """

    player = Player()

    result = player.devices()

    for device in result.values():
        click.echo(device[1])


@player.command()
def transfer():
    """Transfer playback to a new device and optionally begin playback

    If no target id is provided, displays list of possible targets
    """

    player = Player()

    result = player.devices()
    for device in result.values():
        click.echo(device[1])

    choice = click.prompt("Provide device number (n) or pass x to exit", type=int)
    if not (id := result.get(choice, None)):
        raise click.Abort()

    result = player.transfer(id[0])

    click.echo(result)


@player.command()
def shuffle():
    """Toggle shuffle on or off for user's playback"""

    player = Player()

    result = player.shuffle()

    click.echo(result)


@player.command()
@click.argument("uri", type=SpotifyURI(), required=False, default=None, nargs=1)
def queue(uri):
    """Get the list of objects that make up the user's queue or add given one

    If no argument is passed, displays current user's queue.
    Otherwise will attempt to add new item to queue. Works only with valid Spotify uri.
    """

    player = Player()

    if not (result := player.queue()):
        click.echo("No active device found")
        return

    if uri:
        result = player.add_queue(uri, id)
        click.echo(result)
        return

    current = result[0]
    queue = result[1:]

    click.echo(f"-> {current}")

    starts = 1
    while queue:
        for idx, i in enumerate(range(5), start=starts):
            try:
                click.echo(f" ({idx}) {queue.pop(i)}")
            except IndexError:
                break
        else:
            click.echo("(more)")
            if not ("y" == click.prompt("Do you want to continue? (y/n)", type=str)):
                raise click.Abort()
            starts += 5
            click.echo("\033[F\033[K" * 7, nl=False)  # clear last line


@player.command()
@click.option(
    "--limit", default=10, type=click.IntRange(1, 50), help="Limit displayed songs"
)
def recent(limit):
    """Displays last -n songs for active session, default 10"""
    player = Player()

    result = player.recent(limit)

    for song in result:
        click.echo(f" \\/ {song}")


cli.add_command(player)

if __name__ == "__main__":
    cli()
