from harmonize.celery import app
from . import spotify
from .models import RecentlyPlayed, SmartPlaylist, SpotifyUser, Track


@app.task
def seed_and_sync_smart_playlists():
    for playlist in SmartPlaylist.objects.all():
        playlist.seed_and_sync()


@app.task
def store_saved_tracks(full_update=False):
    known_tracks = set(Track.objects.values_list('spotify_uri', flat=True))

    for user in SpotifyUser.objects.all():
        saved = set()

        data = spotify.get_saved_tracks(user)
        for track_data in data:
            saved.add(track_data['uri'])
            if track_data['uri'] not in known_tracks or full_update:
                Track.objects.import_from_spotify(track_data)

        user.tracks.set(Track.objects.filter(spotify_uri__in=saved))

    Track.objects.normalize_ages()
    Track.objects.normalize_tempos()


@app.task
def transition_saved_albums_to_tracks():
    for user in SpotifyUser.objects.all():
        album_uris = []
        for album in spotify.get_saved_albums(user):
            album_uris.append(album['uri'])
            track_uris = [t['uri'] for t in album['tracks']['items']]
            spotify.add_saved_tracks(user, track_uris)

        spotify.remove_saved_albums(album_uris, user)


@app.task
def store_recently_played():
    for user in SpotifyUser.objects.all():
        RecentlyPlayed.objects.store_recently_played(user)
