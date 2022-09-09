"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from .views import AuthURL, SongView, SpotifyCallback, IsAuthenticated, GeneratePlaylist
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'songs', SongView, 'song')

urlpatterns = [
    path('get-auth-url', AuthURL.as_view()),
    path('redirect', SpotifyCallback.as_view()),
    path('is-authenticated', IsAuthenticated.as_view()),
    path('generate', GeneratePlaylist.as_view()),
    path('api/', include(router.urls)),
]
