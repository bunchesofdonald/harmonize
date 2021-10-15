from django.contrib import admin

from .models import Artist, Album, Track, SmartPlaylist, SpotifyUser


def seed_and_sync_playlists(modeladmin, request, queryset):
    for playlist in queryset:
        playlist.seed_and_sync()


seed_and_sync_playlists.short_description = "Sync playlist with Spotify"


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "spotify_uri")
    search_fields = ("name",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("name", "release_date", "spotify_uri")
    search_fields = ("name",)
    list_filter = ("artists",)


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "album", "spotify_uri")
    search_fields = ("name",)


@admin.register(SmartPlaylist)
class SmartPlaylist(admin.ModelAdmin):
    list_display = (
        "name", "spotify_uri", "track_filter", "candidate_count", "user")
    actions = [seed_and_sync_playlists, ]
    raw_id_fields = ['seed']
    readonly_fields = ('candidate_artists', )

    fieldsets = (
        ('None', {
            'fields': (
                'spotify_uri',
                'name',
                'track_limit',
                'track_filter',
                'user',
                'seed',
                'candidate_artists'
            )
        }),
    )

    def candidate_artists(self, obj):
        return ', '.join(
            Artist.objects
                  .filter(albums__tracks__in=obj.candidates)
                  .distinct()
                  .values_list('name', flat=True)
        )

    def candidate_count(self, obj):
        return len(obj.candidates)


@admin.register(SpotifyUser)
class SpotifyUserAdmin(admin.ModelAdmin):
    pass
