import base64
import requests
import uuid

from django.conf import settings
from django.core.cache import cache

API_URL = "https://api.spotify.com/v1"


def basic_auth_headers():
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET
    encoded_client = base64.b64encode(
        f"{client_id}:{client_secret}".encode("utf-8")
    ).decode("utf-8")
    return {"Authorization": f"Basic {encoded_client}"}


def bearer_auth_headers():
    token = cache.get("spotify:access_token")
    return {"Authorization": f"Bearer {token}"}


def memoize(func):
    def wrapper(*args):
        key = ":".join(["spotify"] + list(args))
        result = cache.get(key)
        if result is None:
            result = func(*args)
            cache.set(key, result, timeout=31_557_600)  # Cache for a year.

        return result

    return wrapper


def authorize_url():
    state = str(uuid.uuid4())
    scopes = [
        'playlist-modify-private',
        'user-library-modify',
        'user-library-read',
        'user-read-recently-played',
        'user-top-read',
    ]

    url = (
        "https://accounts.spotify.com/authorize/"
        f"?client_id={settings.SPOTIFY_CLIENT_ID}"
        "&response_type=code"
        "&redirect_uri=http://azul:9110/auth/complete/"
        f"&scope={' '.join(scopes)}"
        f"&state={state}"
    )

    return url


def get_tokens(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost/callback/",
    }

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers=basic_auth_headers(),
        data=data,
    )

    tokens = resp.json()

    cache.set("spotify:access_token", tokens["access_token"], timeout=None)
    cache.set("spotify:refresh_token", tokens["refresh_token"], timeout=None)

    return tokens


def refresh_access_token():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": cache.get("spotify:refresh_token"),
    }

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers=basic_auth_headers(),
        data=data,
    )

    token_data = resp.json()
    cache.set("spotify:access_token", token_data["access_token"], timeout=None)

    return token_data


def api_call(url, method="get", payload=None, decode_response=True, user=None, auth_headers=None):
    if method == "delete":
        request_func = requests.delete
        args = (url,)
        kwargs = {"json": payload}
    elif method == "post":
        request_func = requests.post
        args = (url,)
        kwargs = {"json": payload}
    elif method == "put":
        request_func = requests.put
        args = (url,)
        kwargs = {"json": payload}
    else:
        request_func = requests.get
        args = (url,)
        kwargs = {}

    if not auth_headers:
        if user:
            auth_headers = user.bearer_auth_headers()
        else:
            auth_headers = basic_auth_headers()

    response = request_func(*args, headers=auth_headers, **kwargs)

    if response.status_code == 401:
        if user:
            user.refresh_access_token()
            auth_headers = user.bearer_auth_headers()
            response = request_func(*args, headers=auth_headers, **kwargs)

    response.raise_for_status()

    if decode_response:
        return response.json()
    else:
        return response


def search(q, search_type="album"):
    return api_call(f"{API_URL}/search?q={q}&type={search_type}")


def get_saved_albums(user):
    def album_generator(url):
        data = api_call(url, user=user)
        next_url = data["next"]
        for album in data["items"]:
            yield album["album"]

        if next_url:
            yield from album_generator(next_url)

    return album_generator(f"{API_URL}/me/albums?limit=50")


def remove_saved_albums(album_uris, user):
    album_ids = [get_object_id(uri) for uri in album_uris]
    chunks = [album_ids[i:i + 50] for i in range(0, len(album_ids), 100)]

    for chunk in chunks:
        api_call(
            f"{API_URL}/me/albums",
            method="delete",
            payload=chunk,
            decode_response=False,
            user=user
        )


def get_saved_tracks(user):
    def track_generator(url):
        data = api_call(url, user=user)
        next_url = data["next"]
        for track in data["items"]:
            yield track["track"]

        if next_url:
            yield from track_generator(next_url)

    return track_generator(f"{API_URL}/me/tracks?limit=50")


def add_saved_tracks(user, track_uris):
    track_ids = [get_object_id(uri) for uri in track_uris]
    chunks = [track_ids[i:i + 50] for i in range(0, len(track_ids), 100)]

    for chunk in chunks:
        api_call(
            f"{API_URL}/me/tracks",
            method="put",
            payload=chunk,
            decode_response=False,
            user=user
        )


def get_playlist(id, user):
    data = api_call(f"{API_URL}/playlists/{id}", user=user)

    def track_generator(data):
        next_url = data["next"]
        for track in data["items"]:
            yield track["track"]

        if next_url:
            yield from track_generator(api_call(next_url, user=user))

    return {
        "uri": data["uri"],
        "name": data["name"],
        "description": data["description"],
        "tracks": track_generator(data["tracks"]),
    }


def get_users_profile():
    return api_call(f"{API_URL}/me")


def get_users_playlists(user):
    return api_call(f"{API_URL}/me/playlists", user=user)


def create_playlist(user, name):
    playlist = api_call(
        f"{API_URL}/users/{user.spotify_id}/playlists",
        method="post",
        payload={"name": name, "public": False},
        user=user
    )
    return playlist["uri"]


def replace_playlist_tracks(user, playlist_id, tracks):
    if len(tracks) > 100:
        raise RuntimeError(
            "The replace tracks API has a maximum of 100 tracks.")

    api_call(
        f"{API_URL}/playlists/{playlist_id}/tracks",
        method="put", payload={"uris": tracks},
        user=user
    )


def add_tracks_to_playlist(playlist_id, tracks):
    chunks = [tracks[i:i + 100] for i in range(0, len(tracks), 100)]

    for chunk in chunks:
        api_call(
            f"{API_URL}/playlists/{playlist_id}/tracks",
            method="post",
            payload={"uris": chunk},
        )


def clear_playlist(playlist_id):
    api_call(
        f"{API_URL}/playlists/{playlist_id}/tracks",
        method="put", payload={"uris": []})


def update_playlist_details(user, playlist_id, data):
    api_call(
        f"{API_URL}/playlists/{playlist_id}/",
        method="put", payload=data, decode_response=False,
        user=user)


@memoize
def get_album(id):
    return api_call(f"{API_URL}/albums/{id}")


def get_artist(id, user):
    return api_call(f"{API_URL}/artists/{id}", user=user)


def get_related_artists(id):
    return api_call(f"{API_URL}/artists/{id}/related-artists")['artists']


def get_audio_features(id, user):
    return api_call(f"{API_URL}/audio-features/{id}", user=user)


def get_recently_played(user):
    data = api_call(f"{API_URL}/me/player/recently-played?limit=50", user=user)

    def item_generator(data):
        next_url = data["next"]
        for item in data["items"]:
            yield item

        if next_url:
            yield from item_generator(api_call(next_url, user=user))

    return item_generator(data)


def get_object_id(uri):
    return uri.split(":")[-1]
