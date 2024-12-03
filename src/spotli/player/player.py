import shutil
from datetime import datetime

from ..base.models import SpotifyURI
from .api import PlayerApi


class Player:
    def __init__(self):
        self.player = PlayerApi()

    def _to_ms(self, time: datetime) -> int:
        """Parses a datetime object into milliseconds

        Args:
            time (datetime): datetime to parse

        Returns:
            int: numerical equivalent of the time in milliseconds
        """
        seconds = time.hour * 60 * 60 + time.minute * 60 + time.second
        return seconds * 1000

    def _format_time(self, time_ms: int) -> str:
        """Parses milliseconds into formated time string

        Args:
            time_ms (int): time in milliseconds to parse

        Returns:
            str: string in correct format
        """
        seconds = time_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _generate_progress_bar(self, duration_ms: int, progress_ms: int) -> str:
        """Generates progress bar that is adjusted to the terminal width

        Args:
            duration_ms (int): length of the song in milliseconds
            progress_ms (int): current song moment in milliseconds

        Returns:
            str: String representation of progress bar
        """
        width: int = None
        fill: str = "█"
        empty: str = "-"

        if width is None:
            width = int(shutil.get_terminal_size().columns * 0.1)

        width = max(10, min(30, width))  # ensure that width is between 10 and 30

        progress = progress_ms / duration_ms if duration_ms > 0 else 0

        bar = width - 2
        filled_char = int(bar * progress)
        empty_char = bar - filled_char

        bar = fill * filled_char + empty * empty_char

        current_time = self._format_time(progress_ms)
        total_time = self._format_time(duration_ms)

        return f"[{bar}] {current_time} / {total_time}"

    def status_short(self) -> str:
        """Displays short description about current device state

        Returns:
            str: string with current device state
        """
        if not (state := self.player.get_playback_state()):
            return "No active device found"

        device = state.device
        song = state.item
        is_playing = "▶️" if state.is_playing else "⏸"

        artists = " x ".join(artist.name for artist in song.artists)
        song_name = song.name
        volume = state.device.volume_percent

        song_by_artist = f"{artists} - {song_name}"

        return f"{is_playing}  '{song_by_artist}' @ {device.name}[{device.id[:5]}] vol: {volume}%"

    def status(self) -> str:
        """Displays long description about current device state

        Returns:
            str: multi-line string with comprehensive device state
        """
        if not (state := self.player.get_playback_state()):
            return "No active device found"

        song = state.item
        device = state.device
        shuffle = "🔀" if state.shuffle_state else "🟦"
        is_playing = "▶️" if state.is_playing else "⏸"
        repeat = {"track": "🔂", "context": "🔁"}.get(state.repeat_state, "🟦")
        volume = state.device.volume_percent

        artists = " x ".join(artist.name for artist in song.artists)
        song_name = song.name

        song_by_artist = f"{artists} - {song_name}"
        progress_bar = self._generate_progress_bar(
            duration_ms=song.duration_ms, progress_ms=state.progress_ms
        )

        return (
            f"\ndevice: {device.name}[{device.id[:5]}]\n"
            + f"{song_by_artist}\n"
            + f"{shuffle} {repeat} {is_playing}  {progress_bar} vol: {volume}%\n"
        )

    def play(self, id: str = None) -> str:
        """Calls spotify api to start playback on given device.
           If no id is given then targets current active device.

        Args:
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: current song
        """
        self.player.start_resume_playback(id)

        result = "▶️" if not id else f"on [{id[:5]}] ▶️"

        return result + self.status_short()[1:]

    def pause(self, id: str = None) -> str:
        """Calls spotify api to pause playback on given device.
           If no id is given then targets current active device.

        Args:
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: current song
        """
        self.player.pause_playback(id)

        result = "⏸" if not id else f"on [{id[:5]}] ⏸"

        return result + self.status_short()[1:]

    def next(self, id: str = None) -> str:
        """Calls spotify api to start next song on given device.
           If no id is given then targets current active device.

        Args:
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: Information about targeted device
        """
        self.player.skip_to_next(id)

        return "Playing next song" + (f" on device [{id[:5]}]" if id else "")

    def previous(self, id: str = None):
        """Calls spotify api to start previous song on given device.
           If no id is given then targets current active device.

        Args:
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: Information about targeted device
        """
        self.player.skip_to_previous(id)

        return "Playing previous song" + (f" on device [{id[:5]}]" if id else "")

    def volume(self, value: int, id: str = None) -> str:
        """Set volume on given level.
           If no id is given then targets current active device.

        Args:
            value (int): percentage level to which to set the volume of the device
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: Information about new volume level
        """
        self.player.set_playback_volume(value, id)

        return f"Setting volume to {value}%" + (f" on device [{id[:5]}]" if id else "")

    def seek(self, time: datetime, id: str = None) -> str:
        """Seeks to the given position in the user's currently playing track.
           If the specified time is outside the range of the song,
           it will jump to the next one

        Args:
            time (datetime): time position to seek to
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: Information about current song playing
        """
        self.player.seek_to_position(self._to_ms(time), id)

        return self.status_short()

    def repeat(self, value: str, id: str = None) -> str:
        """Set the repeat mode for the user's playback
        `track` - repeat current track
        `context` - repeat current context (album, queue)
        `off` - turns off repeat mode

        Args:
            value (str): repeat mode {track|context|off}
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: Information about repeat state mode
        """
        self.player.set_repeat_mode(value.lower(), id)

        return f"repeat mode set to: {value}"

    def devices(self) -> dict[int, tuple[str, str]]:
        """Get information about a user's available Spotify Connect devices

        Returns:
            dict[int, tuple[str, str]]: dict[num : (device id, device description)]
        """
        devices = {}

        for i, device in enumerate(self.player.get_available_devices(), start=1):
            id = device.id
            active = "🟢" if device.is_active else "🔴"
            private = "🙈" if device.is_private_session else "🐵"
            restricted = "🔐" if device.is_restricted else "🔓"
            name = device.name
            device_type = device.type

            devices[i] = (
                id,
                f"({i}) {active} [{id}] {private} {restricted} {name} @ {device_type}",
            )

        return devices

    def transfer(self, id: str) -> str:
        """Transfer playback to a new device

        Args:
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: Target device
        """
        self.player.transfer_playback(id)

        return f"Transferring playback to {id[:5]}"

    def shuffle(self, id: str = None) -> str:
        """Toggle shuffle on or off for user's playback

        Args:
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: Shuffle state set
        """
        if not (state := self.player.get_playback_state()):
            return "No active device found"

        shuffle_state = not state.shuffle_state

        self.player.toggle_playback_shuffle(shuffle_state, id)

        return f"Setting shuffle state to {shuffle_state}"

    def queue(self) -> list[str]:
        """Get the list of objects that make up the user's queue

        Returns:
            list[str]: List of tracks in queue
        """
        queue = self.player.get_user_queue()

        if not queue:
            return None

        queue = [
            " x ".join(artist.name for artist in q.artists) + " - " + q.name
            for q in queue
        ]

        return queue

    def add_queue(self, uri: SpotifyURI, id: str = None) -> str:
        """Add an item to the end of the user's current playback queue

        Args:
            uri (SpotifyURI): Valid Spotify URI track
            id (str, optional): device id to target while making api call. Defaults to None.

        Returns:
            str: Spotify URI of added song
        """
        self.player.add_item_to_queue(uri, id)

        return f"Added {uri} to queue"

    def recent(self, limit: int) -> list[str]:
        """Get tracks from the current user's recently played tracks

        Args:
            limit (int): The maximum number of items to return

        Returns:
            list[str]: List of tracks
        """
        result = self.player.get_recently_played_tracks(limit)

        songs = []

        for track in result:
            artists = " x ".join(artist.name for artist in track.artists)
            song_name = track.name
            songs += [f"{artists} - {song_name}"]

        return songs
