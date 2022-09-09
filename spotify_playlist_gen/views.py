from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from requests import Request, post
from .util import update_or_create_user_tokens, is_spotify_authenticated
from .serializers import SongSerializer, PlaylistSerializer
from .models import Song
from django.conf import settings
import random
import requests
import json

SPOTIFY_SECRET_KEY = settings.SPOTIFY_SECRET_KEY
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
REDIRECT_URI = settings.REDIRECT_URI
scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-modify-public'


class AuthURL(APIView):
    def get(self, request, format=None):
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scope,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url
        return Response({'url': url}, status=status.HTTP_200_OK)


class SpotifyCallback(APIView):
    def get(self, request, format=None):
        code = request.GET.get('code')
        error = request.GET.get('error')
        response = post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }).json()
        access_token = response.get('access_token')
        token_type = response.get('token_type')
        refresh_token = response.get('refresh_token')
        expires_in = response.get('expires_in')
        error = response.get('error')
        if not request.session.exists(request.session.session_key):
            request.session.create()
        update_or_create_user_tokens(request.session.session_key, access_token, token_type, expires_in, refresh_token)
        return redirect(f'http://localhost:3000/auth/{access_token}/{refresh_token}')


class IsAuthenticated(APIView):
    def get(self, request, format=None):
        token = request.META.get('HTTP_AUTHORIZATION')
        token = token.split()
        token = token[1]
        is_authenticated = is_spotify_authenticated(token)

        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


class SongView(viewsets.ModelViewSet):
    serializer_class = SongSerializer
    queryset = Song.objects.all()


class GeneratePlaylist(APIView):
    def post(self, request, format=None):
        serializer = PlaylistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_data = serializer.validated_data['token']
        user_id = serializer.validated_data['user_id']
        track_id = serializer.validated_data['track_id']
        track_name = serializer.validated_data['track_name']
        artist_id = serializer.validated_data['artist_id']
        artist_name = serializer.validated_data['artist_name']
        custom_playlist_name = serializer.validated_data.get('playlist_name')

        def fetch_artist_genre(artist_id):
            endpoint_url = f'https://api.spotify.com/v1/artists/{artist_id}'
            query = f'{endpoint_url}'
            response = requests.get(query,
                                    headers={"Content-Type": "application/json",
                                             "Authorization": f"Bearer {token_data}"})
            json_response = response.json()
            genres = json_response['genres']
            try:
                index = random.randint(0, len(genres) - 1)
            except:
                error = "Spotify doesn't store genres for this artist, please try another one!"
                return Response({error: error}, status=status.HTTP_400_BAD_REQUEST)

            genre = genres[index]
            return genre

        def query_api(seeds):
            filters = define_filters(seeds)
            query = f'https://api.spotify.com/v1/recommendations?limit={filters[0]}&market={filters[1]}&seed_genres={filters[2]}'
            query += f'&seed_artists={filters[3]}'
            query += f'&seed_tracks={filters[4]}'
            response = requests.get(query,
                                    headers={"Content-Type": "application/json",
                                             "Authorization": f"Bearer {token_data}"})
            json_response = response.json()
            return json_response

        def define_filters(seeds):
            limit = 30
            market = "GB"
            seed_artists = seeds[0]
            seed_tracks = seeds[1]
            seed_genres = seeds[2]
            filters = [limit, market, seed_genres, seed_artists, seed_tracks]
            return filters

        def create_playlist(artist, track, playlist_name=None):
            if playlist_name is None:
                playlist_name = f"Playlist generated based on {track} by {artist}"
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token_data}'}
            response = post(f'https://api.spotify.com/v1/users/{user_id}/playlists',
                            data=json.dumps({'name': playlist_name}),
                            headers=headers).json()

            # import pdb; pdb.set_trace()
            return response.get('id')

        def add_tracks_to_playlist(json_response, playlist_id, ):
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token_data}'}
            uris = []
            for i, j in enumerate(json_response['tracks']):
                uris.append(j['uri'])

            response = post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                            data=json.dumps({'uris': uris}), headers=headers)
            return

        genre = fetch_artist_genre(artist_id)
        seeds = [artist_id, track_id, genre]
        json_response = query_api(seeds)
        playlist_id = create_playlist(artist_name, track_name, custom_playlist_name)
        add_tracks_to_playlist(json_response, playlist_id)

        return Response({'message': 'POST request success',
                         'playlist_id': playlist_id,
                         }, status=status.HTTP_200_OK)
