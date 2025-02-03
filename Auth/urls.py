from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path("register/",RegisterUser.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/', ListUsersView.as_view()),
    path("channel", ChannelApiView.as_view()),
    path('user/', userInfoView.as_view()),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/<id>', verifyEmailView.as_view()),
    path("googlesignin", googleSigninApi.as_view()),
    path("mychannel/",myChannelView.as_view()),
    path("history/",ListHistoryView.as_view()),
    path("resendemail/",ResendEmailView.as_view()),
    path("changepassword/",ChangePasswordView.as_view()),
    path("edit_profile/",EditProfileView.as_view())
]
