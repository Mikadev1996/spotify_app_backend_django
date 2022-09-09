from rest_framework import serializers
from .models import Song


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'artist', 'description')


class PlaylistSerializer(serializers.Serializer):
    artist = serializers.CharField()
    track = serializers.CharField()
    token = serializers.CharField()
    user_id = serializers.CharField()
    playlist_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
