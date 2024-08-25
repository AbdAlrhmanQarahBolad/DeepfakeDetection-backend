from django.urls import path
from .views import *
from .views import CreateUserAPI,UpdateUserAPI,SaveUserVoiceAPI,GetRandomSatementAPI,GetRandomStatementLoginAPI
from .views import CreateCallAPI,CallUpdateView,CallCheckView,IsDeepFakeAudioAPI
from knox.views import LogoutView,LogoutAllView


urlpatterns = [
    path('create-user/',CreateUserAPI.as_view()),
    path('update-user/<int:pk>/',UpdateUserAPI.as_view()),
    path('login-user/',LoginUserAPI.as_view()),
    path('logout-user/',LogoutView.as_view()),
    path('logoutall-user/',LogoutAllView.as_view()),
    path('login-user-voice/',VoiceLoginUserAPI.as_view()),
    path('voice/save/',SaveUserVoiceAPI.as_view()),
    path('text/generate/',GetRandomStatementLoginAPI.as_view()),#post
    path('text/generate/public/',GetRandomSatementAPI.as_view()),#get
    path('calls/create/',CreateCallAPI.as_view()),
    path('calls/close/<int:pk>',CallUpdateView.as_view()),
    path('calls/voice/check/<int:pk>',CallCheckView.as_view()),
    path('calls/accept-or-decline',AcceptDeclineIncomingCalles.as_view()),
    path('check/audio/',IsDeepFakeAudioAPI.as_view())
]
