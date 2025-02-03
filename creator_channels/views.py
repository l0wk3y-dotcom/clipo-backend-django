from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from Auth.models import CreatorChannel
from rest_framework import generics
from videos.serializers import VideoSerializer
from Auth.serializers import CreatorChannelSerializer
# Create your views here.

class ListChannelsVIew(APIView):
    def get(self, request, category = None, *args, **kwargs):
        if not category:
            qs = CreatorChannel.objects.all()
        else:
            qs = CreatorChannel.objects.filter(category__icontains = category)
        sz = CreatorChannelSerializer(qs, many = True)

        return Response(sz.data)

class ListChannelVideosVIew(APIView):
    def get(self, request, id, *args, **kwargs):
        channel = get_object_or_404(CreatorChannel, id = id)
        videos = channel.user.videos.all()
        sz = VideoSerializer(videos, many = True)
        return Response(sz.data)
    
class retrieveChannelsView(generics.RetrieveAPIView):
    lookup_field = "id"
    serializer_class = CreatorChannelSerializer
    queryset = CreatorChannel.objects.all()