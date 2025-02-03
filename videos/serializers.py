from rest_framework.serializers import *
from .models import *
from Auth.serializers import CreatorChannelSerializer

class VideoSerializer(ModelSerializer):
    liked = SerializerMethodField()
    channel = SerializerMethodField()
    class Meta:
        model = Video
        exclude = ["creator", "liked_by"]
    def get_channel(self, obj, *args, **kwargs):
        return CreatorChannelSerializer(obj.creator.creatorchannel).data
    
    def get_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False  #

class PlaylistSerializer(ModelSerializer):
    video_count = SerializerMethodField()
    class Meta:
        model = Playlists
        fields = ['user','videos','name','description','picture','video_count',"id"]
        extra_kwargs = {
            'videos' : {'write_only' : True, 'required' : False}
        }
    
    def get_video_count(self, obj, *args, **kwargs):
        return obj.videos.all().count()
    
class PlaylistFullSerializer(ModelSerializer):
    videos = VideoSerializer(many = True)
    class Meta:
        model = Playlists
        fields = ['user','videos','name','description','picture',"id"]
