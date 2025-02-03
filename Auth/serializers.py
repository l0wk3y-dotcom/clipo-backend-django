from rest_framework.serializers import *
from .models import *
from videos.models import Video

class LastWatchSerializer(ModelSerializer):
    channel = SerializerMethodField()
    class Meta:
        model = Video
        fields = ["title","id","image","channel"]

    def get_channel(self, obj, *args, **kwargs):
        return CreatorChannelSerializer(obj.creator.creatorchannel).data
    


class SelfUserModelSerializer(ModelSerializer):
    last_watched = SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ["email","is_creater","is_active","name","username","profile_picture","age","last_watched"]
    def get_last_watched(self, obj, *args, **kwargs):
        return LastWatchSerializer(obj.history.order_by("-id").first()).data

class EditUserModelSerializer(ModelSerializer):
    profile_picture = ImageField(required=False)
    class Meta:
        model = CustomUser
        fields = ["name","profile_picture","age"]

class UserModelSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email","is_creater","is_active","name","username","profile_picture","age"]

class RegisterUserSerializer(ModelSerializer):
    password = CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ["email","name","username","age","profile_picture","password", "confirm_password"]
    
    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise ValidationError("Passwords should be the same")
        return data
        
    def create(self, validated_data):
        password = validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CreatorChannelSerializer(ModelSerializer):
    creater = SerializerMethodField()
    user =PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True, # Maps `user_id` to the `user` field in the model
    )
    class Meta:
        model = CreatorChannel
        fields = "__all__"
    
    def get_creater(self, obj):
        return UserModelSerializer(obj.user).data
    
