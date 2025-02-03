from django.db.models.query import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .pagination import DefaultPaginationClass
from .models import *
from time import sleep
from .serializers import *


class ListCreateVideosView(generics.ListCreateAPIView):
    queryset = Video.objects.order_by('-created_at')[:3]
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsAuthenticated()]
        else:
            return [AllowAny()]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Pass the user directly to the serializer's save method
        serializer.save(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class RetrieveUpdateVideosView(generics.RetrieveUpdateAPIView):
    serializer_class = VideoSerializer
    lookup_field = "id"
    queryset = Video.objects.all()

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            video = self.get_object()
            request.user.history.add(video)
            video.views = video.views + 1
            video.save()
        return super().retrieve(request, *args, **kwargs)

class PopularVideosView(generics.ListAPIView):
    pagination_class = DefaultPaginationClass
    queryset = Video.objects.order_by('-views')[:20]
    serializer_class = VideoSerializer
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class TrendingVideosView(generics.ListAPIView):
    pagination_class = DefaultPaginationClass
    queryset = sorted(Video.objects.order_by('-created_at')[:1000], key=lambda video: video.views, reverse=True)[:20]
    serializer_class = VideoSerializer
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class PlaylistsListView(generics.ListCreateAPIView):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        playlists = Playlists.objects.filter(user = self.request.user)
        return playlists
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # Add the user ID to the data
        data["user"] = request.user.id
        
        # Use the serializer explicitly with the modified data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class PlaylistView(generics.RetrieveAPIView):
    serializer_class = PlaylistFullSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.playlists
    


class VideoListView(generics.ListAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        videos = Video.objects.filter(creator = self.request.user)
        return videos
    
    

class CategoryFilter(APIView):
    def get(self, request, category, *args, **kwargs):
        qs = Video.objects.filter(tags__icontains = category)
        sz = VideoSerializer(qs ,many = True)

        return Response(sz.data)


class LikeVideoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, *args, **kwargs):
        user = request.user
        video = get_object_or_404(Video, id = id)
        if user.favourites.filter(id = id).exists():
            user.favourites.remove(video)
            return Response({"status" : "unliked"}, status=status.HTTP_200_OK)
        else:
            user.favourites.add(video)
            return Response({"status" : "liked"}, status=status.HTTP_200_OK)
 

class LikedVideosListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        qs = request.user.favourites.all()
        sz = VideoSerializer(qs, many = True, context={'request': request})
        return Response(sz.data)
    

class SearchVideoView(APIView):
    def get(self, request, query, *args, **kwargs):
        qs = Video.objects.filter(Q(title__icontains=query) | Q(tags__icontains=query))
        sz = VideoSerializer(qs, many=True)

        return Response(sz.data)
    
class AddToPlaylistView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,id,videoid, *args, **kwargs):
        playlist = get_object_or_404(Playlists, id = id)
        
        if playlist.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        videoobj = get_object_or_404( Video, id = videoid)
        if playlist.videos.filter(id = videoid).exists():
            return Response({"message" : "video Already in the playlist"}, status=status.HTTP_400_BAD_REQUEST)
        playlist.videos.add(videoobj)
        return Response({"message" : "video created succesfully"}, status=status.HTTP_200_OK)
    
class RemoveFromPlaylistView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,id,videoid, *args, **kwargs):
        playlist = get_object_or_404(Playlists, id = id)
        
        if playlist.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        videoobj = get_object_or_404( Video, id = videoid)
        if not playlist.videos.filter(id = videoid).exists():
            return Response({"message" : "video is not in playlist"}, status=status.HTTP_400_BAD_REQUEST)
        playlist.videos.remove(videoobj)
        return Response({"message" : "video removed succesfully"}, status=status.HTTP_200_OK)
        
    
