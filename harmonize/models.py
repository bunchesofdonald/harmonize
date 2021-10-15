from dateutil.parser import parse
from datetime import timedelta
import logging
import math
import random
import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import dateparse, timezone
from django.utils.functional import cached_property

from . import spotify


log = logging.getLogger(__name__)


SIMILARITY_FEATURES = [
    ('age', 'g', 1),
    ('acousticness', 'a', 1),
    ('compressed_tempo', 't', 1),
    ('danceability', 'd', 1),
    ('energy', 'e', 1),
    ('instrumentalness', 'i', 1),
    ('valence', 'v', 1),
]


def oxford_join(items):
    items = list(items)
    start = ', '.join(items[:-1])
    return ', and '.join([start, items[-1]])


class SpotifyObject(models.Model):
    name = models.CharField(max_length=255)
    spotify_uri = models.CharField(max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True

    @property
    def spotify_id(self):
        return spotify.get_object_id(self.spotify_uri)

    @property
    def kind(self):
        return self.spotify_uri.split(":")[1]

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.TextField()


class ArtistQuerySet(models.QuerySet):
    def import_from_spotify(self, data, update=False):
        assert data["type"] == "artist"
        artist, created = self.update_or_create(
            spotify_uri=data["uri"], defaults={"name": data["name"]}
        )

        if created or update:
            if genres := data.get('genres', []):
                artist.genres.set([
                    Genre.objects.get_or_create(name=genre)[0]
                    for genre in genres
                ])
                log.warning(
                    "Set artist genres. artist='%s' genres=%s",
                    artist.name, genres
                )

        return artist


class Artist(SpotifyObject):
    genres = models.ManyToManyField(Genre)
    objects = ArtistQuerySet.as_manager()

    class Meta:
        ordering = ("name", )


class AlbumQuerySet(models.QuerySet):
    def import_from_spotify(self, data):
        assert data["type"] == "album"

        artists = []
        for artist_data in data["artists"]:
            artists.append(Artist.objects.import_from_spotify(artist_data))

        try:
            release_date = parse(data["release_date"])
        except KeyError:
            release_date = None

        album, created = self.get_or_create(
            spotify_uri=data["uri"],
            defaults={
                "name": data["name"],
                "image_url": data["images"][0]["url"],
                "release_date": release_date,
            },
        )

        album.artists.set(artists)

        return album


class Album(SpotifyObject):
    artists = models.ManyToManyField(Artist, related_name="albums")
    release_date = models.DateField(null=True, blank=True)
    image_url = models.CharField(max_length=255)

    objects = AlbumQuerySet.as_manager()

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}'


class TrackQuerySet(models.QuerySet):
    def import_from_spotify(self, data):
        assert data["type"] == "track"

        album = Album.objects.import_from_spotify(data["album"])

        track, created = self.update_or_create(
            spotify_uri=data["uri"],
            defaults={
                "name": data["name"],
                "duration_ms": data["duration_ms"],
                "album": album
            },
        )

        if created:
            track.set_audio_features()

        return track

    def normalize_ages(self):
        max_year = Track.objects.aggregate(
            date=models.Max('album__release_date'))['date'].year
        min_year = Track.objects.aggregate(
            date=models.Min('album__release_date'))['date'].year

        for album in Album.objects.all():
            age = (album.release_date.year - min_year) / (max_year - min_year)
            self.filter(album=album).update(age=age)

    def normalize_tempos(self):
        max_tempo = Track.objects.aggregate(
            tempo=models.Max('tempo'))['tempo']
        min_tempo = Track.objects.aggregate(
            tempo=models.Min('tempo'))['tempo']

        self.update(compressed_tempo=(
            (models.F('tempo') - min_tempo) / (max_tempo - min_tempo)
        ))


class Track(SpotifyObject):
    album = models.ForeignKey(
        Album, related_name="tracks", on_delete=models.CASCADE)
    duration_ms = models.PositiveIntegerField()
    added_date = models.DateField(auto_now_add=True)

    age = models.FloatField(null=True)
    compressed_tempo = models.FloatField(null=True)
    acousticness = models.FloatField(null=True)
    danceability = models.FloatField(null=True)
    energy = models.FloatField(null=True)
    instrumentalness = models.FloatField(null=True)
    key = models.PositiveIntegerField(null=True)
    liveness = models.FloatField(null=True)
    loudness = models.FloatField(null=True)
    mode = models.PositiveIntegerField(null=True)
    speechiness = models.FloatField(null=True)
    tempo = models.FloatField(null=True)
    valence = models.FloatField(null=True)

    objects = TrackQuerySet.as_manager()

    class Meta:
        ordering = ("album__name",)

    def set_audio_features(self):
        features = ['acousticness', 'danceability', 'energy',
                    'instrumentalness', 'key', 'liveness', 'loudness', 'mode',
                    'speechiness', 'tempo', 'valence']

        user = SpotifyUser.objects.get_service_user()
        values = spotify.get_audio_features(self.spotify_id, user=user)
        for feature in features:
            setattr(self, feature, values[feature])

        self.save()

    def all_neighbors(self, tracks=None):
        return sorted(get_distances(self, tracks), key=lambda d: d[0])


class SpotifyUserQuerySet(models.QuerySet):
    def import_from_spotify(self, user, data):
        assert data["type"] == "user"
        user, created = self.update_or_create(
            spotify_uri=data["uri"],
            defaults={
                "user": user,
                "name": data["display_name"]
            }
        )

        return user

    def get_service_user(self):
        return self.get(spotify_uri=settings.SPOTIFY_SERVICE_USER_URI)


class SpotifyUser(SpotifyObject):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()

    tracks = models.ManyToManyField(Track, blank=True)

    objects = SpotifyUserQuerySet.as_manager()

    def bearer_auth_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def refresh_access_token(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers=spotify.basic_auth_headers(),
            data=data,
        )

        token_data = resp.json()

        self.access_token = token_data['access_token']
        self.save()

        return token_data


class SmartPlaylist(SpotifyObject):
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    track_limit = models.IntegerField(default=75)
    track_filter = models.JSONField()

    seed = models.ForeignKey(
        Track, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.spotify_uri:
            self.spotify_uri = spotify.create_playlist(self.user, self.name)

        super().save(*args, **kwargs)

        try:
            del self.similar
            del self.candidates
        except AttributeError:
            pass

    def get_new_seed(self):
        return random.choice(self.candidates)

    def seed_and_sync(self):
        self.seed = self.get_new_seed()
        self.save()

        PlaylistHistory.objects.update_history(self)

        self.sync()

    @cached_property
    def candidates(self):
        candidates = self.user.tracks.filter(**self.track_filter)
        candidate_count = len(candidates)

        excluded_tracks = set()
        if candidate_count > self.track_limit:
            exclude_count = int(candidate_count * 0.2)
            excluded_tracks = set(
                self.track_history
                    .order_by('-added_date')
                    .values_list('track_id', flat=True)[:exclude_count]
            )

        return [
            track for track in candidates
            if track.id not in excluded_tracks
        ]

    @cached_property
    def similar(self):
        neighbor_ids = []
        distances = []
        neighboring_tracks = self.seed.all_neighbors(
            self.candidates)[:self.track_limit]
        for distance, neighbor in neighboring_tracks:
            distances.append(distance)
            neighbor_ids.append(neighbor.id)

        return {
            'average_distance': round(sum(distances) / len(distances), 3),
            'tracks': self.user.tracks.filter(id__in=neighbor_ids),
        }

    @property
    def average_distance(self):
        return self.similar['average_distance']

    @property
    def tracks(self):
        return self.similar['tracks']

    @property
    def unique_artists(self):
        return Artist.objects.filter(
            albums__tracks__in=self.tracks
        ).annotate(
            track_count=models.Count('albums__tracks')
        ).order_by('-track_count')

    @property
    def candidate_artists(self):
        return Artist.objects.filter(
            albums__tracks__in=self.candidates
        ).order_by('name')

    @property
    def full_name(self):
        return f'{self.name} (μ{self.average_distance})'

    @property
    def description(self):
        artists = oxford_join(
            self.unique_artists.values_list('name', flat=True)[:3])
        return f'Seeded from "{self.seed.name}". Featuring {artists}.'

    def sync(self):
        today = timezone.now().date().isoformat()
        uris = [track.spotify_uri for track in self.tracks]
        spotify.replace_playlist_tracks(self.user, self.spotify_id, uris)
        spotify.update_playlist_details(self.user, self.spotify_id, {
            'name': self.full_name,
            'description': f'{self.description} Synced {today}.'
        })


class PlaylistHistoryManager(models.Manager):
    def update_history(self, playlist):
        for track in playlist.tracks:
            PlaylistHistory.objects.create(playlist=playlist, track=track)


class PlaylistHistory(models.Model):
    playlist = models.ForeignKey(
        SmartPlaylist,
        related_name='track_history',
        on_delete=models.CASCADE
    )
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    added_date = models.DateField(auto_now_add=True)

    objects = PlaylistHistoryManager()

    class Meta:
        index_together = ('playlist', 'track', 'added_date')


class RecentlyPlayedQuerySet(models.QuerySet):
    def store_recently_played(self, user, last_update=None):
        if not last_update:
            last_update = timezone.now() - timedelta(days=7)

        for item in spotify.get_recently_played(user):
            played_at = dateparse.parse_datetime(item['played_at'])
            if played_at > last_update:
                track = Track.objects.import_from_spotify(item['track'])
                self.get_or_create(user=user, track=track, played_at=played_at)
            else:
                break


class RecentlyPlayed(models.Model):
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    played_at = models.DateTimeField()

    objects = RecentlyPlayedQuerySet.as_manager()

    def __str__(self):
        played_at = self.played_at.isoformat()
        return f'{self.track.name} {played_at} ({self.user.name})'


def distance(a, b):
    distances = []

    a_artists = set(a.album.artists.values_list('name', flat=True))
    b_artists = set(b.album.artists.values_list('name', flat=True))

    if len(a_artists & b_artists) == 0:
        a_genres = set(
            Genre.objects.filter(artist__name__in=a_artists)
                         .values_list('name', flat=True)
        )
        b_genres = set(
            Genre.objects.filter(artist__name__in=b_artists)
                         .values_list('name', flat=True)
        )

        genre_count = len(a_genres | b_genres)
        shared_count = len(a_genres & b_genres)

        if genre_count and shared_count:
            distance = ((1 - (shared_count / genre_count)) ** 2) * 1
            distances.append(distance ** 2)

    for feature, _, weight in SIMILARITY_FEATURES:
        square = (abs(getattr(a, feature) - getattr(b, feature)) ** 2) * weight
        distances.append(square)

    return round(math.sqrt(sum(distances)), 3)


def get_distances(track, tracks=None):
    if not tracks:
        tracks = Track.objects.all()
    distances = []
    for other in tracks:
        distances.append(
            (distance(track, other), other))

    return distances
