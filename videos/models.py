from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=40)
    creator = models.ForeignKey(User, related_name="videos", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateField(auto_now=True)
    views = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name="favourites")
    image = models.ImageField(upload_to=f"images")
    video = models.FileField(upload_to=f"videos")
    tags = models.CharField(max_length=200)

    def get_tags(self):
        return self.tags.split(',')
    
    def __str__(self):
        return self.title

class Playlists(models.Model):
    user = models.ForeignKey(User, related_name="playlists", on_delete=models.CASCADE, blank=True)
    videos = models.ManyToManyField("videos.Video", blank=True, related_name='playlists')
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    picture = models.ImageField(upload_to="playlist_pics", default="playlist_pics/default_playlist.png")
    def __str__(self):
        return self.name
