import argparse
import math
from datetime import datetime, timezone
from time import timezone
from typing import Dict, Optional, Tuple

import spotipy
from dateutil import parser
from spotipy.oauth2 import SpotifyOAuth

SCOPES = [
    "user-library-read",
    "playlist-modify-public",
    "user-read-private",
    "playlist-read-private",
    "user-library-modify",
    "playlist-read-collaborative",
    "playlist-modify-private",
]

SPRING = "Spring"
SUMMER = "Summer"
FALL = "Fall"
WINTER = "Winter"

MAX_TRACKS_PER_PLAYLIST_REQUEST = 100


def first_day_of_spring(year: int) -> datetime:
    """
    First meteorological day of spring is March 1
    """
    return datetime(year=year, month=3, day=1, tzinfo=timezone.utc)


def first_day_of_summer(year: int) -> datetime:
    """
    First meteorological day of summer is June 1
    """
    return datetime(year=year, month=6, day=20, tzinfo=timezone.utc)


def first_day_of_fall(year: int) -> datetime:
    """
    First meteorological day of fall is Sept 22
    """
    return datetime(year=year, month=9, day=22, tzinfo=timezone.utc)


def first_day_of_winter(year: int) -> datetime:
    """
    First meteorological day of winter is Dec 21
    """
    return datetime(year=year, month=12, day=21, tzinfo=timezone.utc)


def get_args():
    parser = argparse.ArgumentParser(description="Creates seasonal playlists for user")
    return parser.parse_args()


def try_get_existing_playlist_id(name: str, sp: spotipy.Spotify) -> Optional[str]:
    total_items = math.inf
    current_offset = 0
    batch_size = 50
    while current_offset < total_items:
        results = sp.current_user_playlists(offset=current_offset)
        total_items = min(results["total"], total_items)
        for item in results["items"]:
            if item["name"] == name:
                return item["id"]
        current_offset += batch_size
    return None


def main():
    args = get_args()
    scopes = SCOPES
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes))
    number_of_tracks = math.inf
    current_offset = 0
    batch_size = 50
    playlists: Dict[str, list[Tuple[str, str, datetime]]] = {}
    seen_ids = set()
    while current_offset < number_of_tracks:
        track_batch = sp.current_user_saved_tracks(
            limit=batch_size, offset=current_offset
        )
        number_of_tracks = min(track_batch["total"], number_of_tracks)
        for item in track_batch["items"]:
            track_added_at: str = item["added_at"]
            added_at_datetime = parser.isoparse(track_added_at)
            track = item["track"]
            track_id: str = track["id"]
            track_name: str = track["name"]

            seen_ids.add(track_id)
            spring_marker = first_day_of_spring(added_at_datetime.year)
            summer_marker = first_day_of_summer(added_at_datetime.year)
            fall_marker = first_day_of_fall(added_at_datetime.year)
            winter_marker = first_day_of_winter(added_at_datetime.year)
            season = None
            year = None
            if added_at_datetime < spring_marker:
                season = WINTER
                year = added_at_datetime.year - 1
            elif spring_marker <= added_at_datetime < summer_marker:
                season = SPRING
                year = added_at_datetime.year
            elif summer_marker <= added_at_datetime < fall_marker:
                season = SUMMER
                year = added_at_datetime.year
            elif fall_marker <= added_at_datetime < winter_marker:
                season = FALL
                year = added_at_datetime.year
            elif winter_marker <= added_at_datetime:
                season = WINTER
                year = added_at_datetime.year
            playlist_name = f"Estaciones: {season} {year}"
            if playlist_name not in playlists:
                playlists[playlist_name] = [(track_name, track_id, added_at_datetime)]
            else:
                playlists[playlist_name].append(
                    (track_name, track_id, added_at_datetime)
                )
        current_offset += batch_size
        print(current_offset, "/", number_of_tracks)
    for playlist_name, tracks in playlists.items():
        existing_playlist_id = try_get_existing_playlist_id(playlist_name, sp)
        track_ids = [track_id for (_, track_id, _) in tracks]
        if not existing_playlist_id:
            print(f'Couldn\'t find a playlist named "{playlist_name}". Creating.')
            playlist_response = sp.user_playlist_create(sp.me()["id"], playlist_name)
            playlist_id = playlist_response["id"]
        else:
            print(f'Found a playlist named "{playlist_name}. Re-using.')
            playlist_id = existing_playlist_id
        if len(track_ids) > MAX_TRACKS_PER_PLAYLIST_REQUEST:
            for i in range(len(track_ids), MAX_TRACKS_PER_PLAYLIST_REQUEST):
                sp.playlist_add_items(
                    playlist_id, track_ids[i : i + MAX_TRACKS_PER_PLAYLIST_REQUEST]
                )
        else:
            sp.playlist_add_items(playlist_id, track_ids)


if __name__ == "__main__":
    main()
