from typing import NoReturn

from ..base.models import SpotifyURI
from ..base.api import SpotifyAPI
from .models import Device, PlaybackState, Track


class PlayerApi:
    def __init__(self):
        self.spotify_api = SpotifyAPI()
        self.endpoint = "me/player"

    def get_playback_state(self) -> PlaybackState | None:
        """Get information about the user's current playback state"""
        endpoint = self.endpoint

        response = self.spotify_api.get(endpoint)

        if response:
            return PlaybackState.from_dict(response)

        return None

    def transfer_playback(self, id: str) -> NoReturn:
        """Transfer playback to a new device"""
        endpoint = self.endpoint

        data = {"device_ids": [id], "play": False}

        self.spotify_api.put(endpoint, data=data)

    def get_available_devices(self) -> list[Device] | None:
        """Get information about a user's available Spotify Connect devices"""
        endpoint = self.endpoint + "/devices"

        response = self.spotify_api.get(endpoint)

        if response:
            return [Device.from_dict(device) for device in response.get("devices")]

        return None

    def get_currently_playing_track(self) -> NoReturn:
        raise NotImplementedError("Not implemented, use get_playback_state() instead")

    def start_resume_playback(self, id: str = None) -> NoReturn:
        """Start a new context or resume current playback on the user's active device"""
        endpoint = self.endpoint + "/play"

        params = {"device_id": id}

        self.spotify_api.put(endpoint, params=params)

    def pause_playback(self, id: str = None) -> NoReturn:
        """Pause playback on the user's account"""
        endpoint = self.endpoint + "/pause"

        params = {"device_id": id}

        self.spotify_api.put(endpoint, params=params)

    def skip_to_next(self, id: str = None) -> NoReturn:
        """Skips to next track in the user's queue"""
        endpoint = self.endpoint + "/next"

        params = {"devide_id": id}

        self.spotify_api.post(endpoint, params=params)

    def skip_to_previous(self, id: str = None) -> NoReturn:
        """Skips to previous track in the user's queue"""
        endpoint = self.endpoint + "/previous"

        params = {"devide_id": id}

        self.spotify_api.post(endpoint, params=params)

    def seek_to_position(self, time: int, id: str = None) -> NoReturn:
        """Seeks to the given position in the user's currently playing track"""
        endpoint = self.endpoint + "/seek"

        params = {"position_ms": time, "devide_id": id}

        self.spotify_api.put(endpoint, params=params)

    def set_repeat_mode(self, value: str, id: str = None) -> NoReturn:
        """Set the repeat mode for the user's playback"""
        endpoint = self.endpoint + "/repeat"

        params = {"state": value, "device_id": id}

        self.spotify_api.put(endpoint, params=params)

    def set_playback_volume(self, value: int, id: str = None) -> NoReturn:
        """Set the volume for the user's current playback device"""
        endpoint = self.endpoint + "/volume"

        params = {"volume_percent": value, "device_id": id}

        self.spotify_api.put(endpoint, params=params)

    def toggle_playback_shuffle(self, state: bool, id: str = None) -> NoReturn:
        """Toggle shuffle on or off for user's playback"""
        endpoint = self.endpoint + "/shuffle"

        params = {"state": state, "device_id": id}

        self.spotify_api.put(endpoint, params=params)

    def get_recently_played_tracks(self, limit: int) -> list[Track] | None:
        """Get tracks from the current user's recently played tracks"""
        endpoint = self.endpoint + "/recently-played"

        params = {
            "limit": limit,
        }

        response = self.spotify_api.get(endpoint, params=params)

        if response:
            return [Track.from_dict(x.get("track")) for x in response.get("items")]

        return None

    def get_user_queue(self) -> list[Track]:
        """Get the list of objects that make up the user's queue"""
        endpoint = self.endpoint + "/queue"

        response = self.spotify_api.get(endpoint) or {}

        currently_playing = Track.from_dict(response.get("currently_playing"))
        queue = [currently_playing] + [
            Track.from_dict(x) for x in response.get("queue")
        ]

        return queue

    def add_item_to_queue(self, uri: SpotifyURI, id: str = None) -> NoReturn:
        """Add an item to the end of the user's current playback queue"""
        endpoint = self.endpoint + "/queue"

        params = {"uri": uri, "id": id}

        self.spotify_api.post(endpoint, params=params)
