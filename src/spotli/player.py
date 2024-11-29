import shutil
from datetime import datetime
from typing import NoReturn

from .commons import SpotifyURI
from .player_models import Device, PlaybackState, Track
from .spotify_api import SpotifyAPI


class PlayerApi:

    def __init__(self):
        self.spotify_api = SpotifyAPI()
        self.endpoint = "me/player"

    def get_playback_state(self) -> PlaybackState | None:

        endpoint = self.endpoint

        response = self.spotify_api.get(endpoint)

        if response:
            return PlaybackState.from_dict(response)

        return None

    def transfer_playback(self, id: str):

        data = {"device_ids" : [id], "play" : False}

        self.spotify_api.put(self.endpoint, data=data)

    def get_available_devices(self):

        endpoint = self.endpoint + "/devices"

        response = self.spotify_api.get(endpoint)

        if response:
            return [Device.from_dict(device) for device in response.get("devices")]

        return None


    def get_currently_playing_track(self):
        raise NotImplementedError("Not implemented, use get_playback_state() instead")

    def start_resume_playback(self, id: str = None) -> NoReturn:

        endpoint = self.endpoint + "/play"

        params = {"device_id": id}

        self.spotify_api.put(endpoint, params=params)

    def pause_playback(self, id: str = None):

        endpoint = self.endpoint + "/pause"

        params = {"device_id": id}

        self.spotify_api.put(endpoint, params=params)

    def skip_to_next(self, id: str = None):

        endpoint = self.endpoint + "/next"

        params = {"devide_id": id}

        self.spotify_api.post(endpoint, params=params)

    def skip_to_previous(self, id: str = None):

        endpoint = self.endpoint + "/previous"

        params = {"devide_id": id}

        self.spotify_api.post(endpoint, params=params)

    def seek_to_position(self, time: int, id: str = None) -> NoReturn:

        endpoint = self.endpoint + "/seek"

        params = {"position_ms": time,
                  "devide_id": id
                 }

        self.spotify_api.put(endpoint, params=params)

    def set_repeat_mode(self, value: str, id: str = None):

        endpoint = self.endpoint + "/repeat"

        params = {"state": value,
                  "device_id": id
                 }

        self.spotify_api.put(endpoint, params=params)

    def set_playback_volume(self, value: int, id: str = None) -> NoReturn:

        endpoint = self.endpoint + "/volume"

        params = {"volume_percent": value,
                  "device_id": id
                 }

        self.spotify_api.put(endpoint, params=params)

    def toggle_playback_shuffle(self, state: bool, id: str = None):

        endpoint = self.endpoint + "/shuffle"

        params = {"state": state,
                  "device_id": id
                 }

        self.spotify_api.put(endpoint, params=params)

    def get_recently_played_tracks(self):
        ...

    def get_user_queue(self):

        endpoint = self.endpoint + "/queue"

        response = self.spotify_api.get(endpoint) or {}

        currently_playing = Track.from_dict(response.get("currently_playing"))
        queue = [Track.from_dict(x) for x in response.get("queue")]

        return (currently_playing, queue)

    def add_item_to_queue(self, uri: SpotifyURI, id: str = None):

        endpoint = self.endpoint + "/queue"

        params = {"uri": uri,
                  "id": id
                 }

        self.spotify_api.post(endpoint, params=params)


class Player:

    def __init__(self):
        self.player = PlayerApi()

    def _to_ms(self, time: datetime) -> int:
        seconds = time.hour * 60 * 60 + time.minute * 60 + time.second
        return seconds * 1000

    def _format_time(self, time_ms: int) -> str:
        seconds = time_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _generate_progress_bar(self, duration_ms: int, progress_ms: int) -> str:
        width: int = None
        fill: str = "█"
        empty: str = "-"

        if width is None:
            width = int(shutil.get_terminal_size().columns * 0.1)

        width = max(10, min(30, width)) # ensure that width is between 10 and 30

        progress = progress_ms / duration_ms if duration_ms > 0 else 0

        bar = width - 2
        filled_char = int(bar * progress)
        empty_char = bar - filled_char

        bar = fill * filled_char + empty * empty_char

        current_time = self._format_time(progress_ms)
        total_time = self._format_time(duration_ms)

        return f"[{bar}] {current_time} / {total_time}"

    def status_short(self) -> str | None:
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
        if not (state := self.player.get_playback_state()):
            return "No active device found"

        song = state.item
        device = state.device
        shuffle = "🔀" if state.shuffle_state else "🟦"
        is_playing = "▶️" if state.is_playing else "⏸"
        repeat = {'track':"🔂", 'context':"🔁"}.get(state.repeat_state, "🟦")
        volume = state.device.volume_percent

        artists = " x ".join(artist.name for artist in song.artists)
        song_name = song.name

        song_by_artist = f"{artists} - {song_name}"
        progress_bar = self._generate_progress_bar(duration_ms=song.duration_ms
                                                   , progress_ms=state.progress_ms)

        return f"\ndevice: {device.name}[{device.id[:5]}]\n" \
             + f"{song_by_artist}\n" \
             + f"{shuffle} {repeat} {is_playing}  {progress_bar} vol: {volume}%\n"

    def play(self, id: str = None) -> str:

        self.player.start_resume_playback(id)

        result = "▶️" if not id else f"on [{id[:5]}] ▶️"

        return result + self.status_short()[1:]

    def pause(self, id: str = None) -> str:

        self.player.pause_playback(id)

        result = "⏸" if not id else f"on [{id[:5]}] ⏸"

        return result + self.status_short()[1:]

    def next(self, id: str = None):

        self.player.skip_to_next(id)

        return "Playing next song" + (f" on device [{id[:5]}]" if id else "")

    def previous(self, id: str = None):

        self.player.skip_to_previous(id)

        return "Playing previous song" + (f" on device [{id[:5]}]" if id else "")

    def volume(self, value: int, id: str = None):

        self.player.set_playback_volume(value, id)

        return f"Setting volume to {value}%" + (f" on device [{id[:5]}]" if id else "")

    def seek(self, time: datetime, id: str = None):

        self.player.seek_to_position(self._to_ms(time), id)

        return self.status_short()

    def repeat(self, value: str, id: str = None):

        self.player.set_repeat_mode(value.lower(), id)

        return f"repeat mode set to: {value}"

    def devices(self) -> dict[int, tuple[str, str]]:

        devices = {}

        for i, device in enumerate(self.player.get_available_devices(), start=1):

            id = device.id
            active = "🟢" if device.is_active else "🔴"
            private = "🙈" if device.is_private_session else "🐵"
            restricted = "🔐" if device.is_restricted else "🔓"
            name = device.name
            device_type = device.type

            devices[i] = (id, f"({i}) {active} [{id}] {private} {restricted} {name} @ {device_type}")

        return devices

    def transfer(self, id: str = None):

        self.player.transfer_playback(id)

        return f"Transferring playback to {id[:5]}"


    def shuffle(self, id: str = None):

        if not (state := self.player.get_playback_state()):
            return "No active device found"

        shuffle_state = not state.shuffle_state

        self.player.toggle_playback_shuffle(shuffle_state, id)

        return f"Setting shuffle state to {shuffle_state}"

    def queue(self):

        currently_playing, queue = self.player.get_user_queue()

        if not currently_playing and not queue:
            return None

        artists = " x ".join(artist.name for artist in currently_playing.artists)
        song_name = currently_playing.name
        current = f"{artists} - {song_name}"

        next = [" x ".join(artist.name for artist in q.artists) + " - " + q.name
                for q in queue]

        return (current, next)

    def add_queue(self, uri: SpotifyURI, id:str = None):

        self.player.add_item_to_queue(uri, id)

        return f"Added {uri} to queue"