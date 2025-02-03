from django.shortcuts import get_object_or_404
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from .serializers import *
from django.contrib.auth.password_validation import get_default_password_validators
from rest_framework.response import Response
from videos.serializers import VideoSerializer
from rest_framework import status
from rest_framework.views import APIView
from .throttles import OnePerMinuteThrottler
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
import random
import string



class RegisterUser(generics.CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = RegisterUserSerializer
    queryset = CustomUser.objects.all()

class ListUsersView(generics.ListAPIView):
    serializer_class = UserModelSerializer
    queryset = CustomUser.objects.all()

class verifyEmailView(APIView):
    def get(self, request, id, *args, **kwargs):
        user = get_object_or_404(CustomUser, secretId = id)
        user.is_active = True
        user.save()

        return Response({"message", "Email verified"},status=status.HTTP_200_OK)

class userInfoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        sz = SelfUserModelSerializer(request.user)
        return Response(sz.data)

        
class googleSigninApi(APIView):
    def post(self, request, *args, **kwargs):
        try:
            token = request.POST.get("id_token")

            if not token:
                return Response({"token is necessart"}, status=status.HTTP_406_NOT_ACCEPTABLE)

            userinfo = id_token.verify_oauth2_token(token, Request(), settings.GOOGLE_WEB_CLIEND_ID )
            email = userinfo["email"]
            picture = userinfo.get('picture')
            username = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
            user, created = CustomUser.objects.get_or_create(email = email, defaults={
                'username' : f"{userinfo["name"]}_{username}",
                'is_active' : True,
                'name' : userinfo["name"],
                'profile_picture' : picture if picture else "profile_pictures/default.jpg"
            })
            if created:
                password =''.join(random.choices(string.ascii_letters + string.digits, k=15)) 
                user.set_password(password)
                user.save()
            
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return Response({"refresh" : str(refresh), "access" : str(access_token)}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"Id token is not valid"}, status=status.HTTP_400_BAD_REQUEST)


class ChannelApiView(generics.ListCreateAPIView):
    serializer_class = CreatorChannelSerializer
    queryset = CreatorChannel.objects.all()

    def get_permissions(self):
        if not self.request.method == "GET":
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        # Make a mutable copy of the request data
        data = request.data.copy()
        # Add the user ID to the data
        data["user"] = request.user.id
        
        # Use the serializer explicitly with the modified data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

class myChannelView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        qs = get_object_or_404(CreatorChannel, user = request.user)
        sz = CreatorChannelSerializer(qs)
        return Response(sz.data)
    

class ListHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VideoSerializer
    
    def get_queryset(self):
        return self.request.user.history.all()
    
class ResendEmailView(APIView):
    throttle_classes = [OnePerMinuteThrottler]
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            user = get_object_or_404(CustomUser, email = email)
            if user.is_active:
                return Response(status=status.HTTP_226_IM_USED)
            send_mail(subject="Email verification", from_email="ha.lowkey.05.ck@gmail.com", recipient_list=[email], message=f"{settings.CLIENT_HOST}/verify/{user.secretId}")
            return Response(status=status.HTTP_302_FOUND)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        password = request.data.get("password")
        confirm_password=  request.data.get("confirm_password")

        user = request.user
        if password == confirm_password:
            user.set_password(password)
            user.save()
            return Response({"message" : "Created succesfully"},status=status.HTTP_202_ACCEPTED)
        return Response({"error" : "Password did not match"}, status=status.HTTP_304_NOT_MODIFIED)

class EditProfileView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        user = CustomUser.objects.get(id = request.user.id)
        sz = EditUserModelSerializer(user, data = request.data, partial = True)
        if sz.is_valid():
            sz.save()
        return Response({"message" : "done"})