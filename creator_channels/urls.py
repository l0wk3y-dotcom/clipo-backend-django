from django.urls import path
from .views import *
urlpatterns = [
    path("",ListChannelsVIew.as_view() ),
    path("category/<str:category>",ListChannelsVIew.as_view() ),
    path("<int:id>/videos/",ListChannelVideosVIew.as_view() ),
     path("<int:id>",retrieveChannelsView.as_view() ),


]