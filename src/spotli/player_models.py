from dataclasses import dataclass
from typing import Any

from .commons import FromDictMixin


@dataclass
class Device(FromDictMixin):
    id: str
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: str
    volume_percent: int
    supports_volume: bool

@dataclass
class Artist(FromDictMixin):
    external_urls: dict[str, str]
    href: str
    id: str
    name: str
    type: str
    uri: str

@dataclass
class Album(FromDictMixin):
    album_type: str
    total_tracks: int
    available_markets: list[str]
    external_urls: dict[str, str]
    id: str
    name: str
    release_date: str
    release_date_precision: str
    uri: str
    artists: list[Artist]

@dataclass
class Track(FromDictMixin):
    album: Album
    artists: list[Artist]
    available_markets: list[str]
    disc_number: int
    duration_ms: int
    external_urls: dict[str, str]
    id: str
    name: str
    popularity: int

@dataclass
class PlaybackState(FromDictMixin):
    device: Device
    repeat_state: str
    shuffle_state: bool
    context: dict[str, Any]
    timestamp: int
    progress_ms: int
    is_playing: bool
    currently_playing_type: str
    item: Track