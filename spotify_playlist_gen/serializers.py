from rest_framework import serializers
from .models import Song


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'artist', 'description')


class PlaylistSerializer(serializers.Serializer):
    artist = serializers.CharField()
    token = serializers.CharField()
    user_id = serializers.CharField()
    track_id = serializers.CharField()
    artist_id = serializers.CharField()
    track_name = serializers.CharField()
    artist_name = serializers.CharField()
    playlist_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
