from django.urls import path
from .views import *
urlpatterns = [
    path("", ListCreateVideosView.as_view()),
    path("<id>/like/", LikeVideoView.as_view()),
    path("<id>", RetrieveUpdateVideosView.as_view()),
    path("category/<category>", CategoryFilter.as_view(), name=""),
    path("popular/", PopularVideosView.as_view()),
    path("trending/", TrendingVideosView.as_view()),
    path("myplaylist/", PlaylistsListView.as_view()),
    path("myplaylist/<int:pk>", PlaylistView.as_view()),
    path("myvideos/", VideoListView.as_view()),
    path("liked/", LikedVideosListView.as_view()),
    path("search/<str:query>", SearchVideoView.as_view()),
    path("playlists/<id>/add/<videoid>", AddToPlaylistView.as_view()),
     path("playlists/<id>/remove/<videoid>", RemoveFromPlaylistView.as_view()),
]

