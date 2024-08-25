
from .serializers import CreateUserSerializer,UpdateUserSerializer,LoginUserSerializer,LoginUserVoiceSerializer,SaveUserVoiceSerializer,GetRandomTextSerializer
from django.contrib.auth import login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.generics import CreateAPIView,UpdateAPIView
from django.contrib.auth.models import User
from knox.auth import TokenAuthentication
from knox import views as knoxViews
from.models import UserVoice,UserStatement,Call,CallStatus,get_user_via_identifier,DeepAudioArchive
from .voice_utils.utils import save_file_into_permanent_folder
from .voice_utils.text_generation import generate_random_arabic_sentence
from .permission_classes import HasRelatedUserStatement,HasRelatedUserVoice
from .permission_classes import CanCreateCallsPermission,HasActiveOrCreatedCallsPermission,IsCallerOrRecipient
from .serializers import CreateCallSerializer,CallSerializer,CallCheckSerializer,AcceptDeclineIncomingCallsSerializer,IsDeepFakeAPISerializer
import os
from knox.models import AuthToken  # Import AuthToken from knox
from .voice_utils.voice_validation import is_deep_fake_audio
from django.contrib.auth.hashers import make_password
from .models import FakeStatus,get_fake_status_name
from django.shortcuts import get_object_or_404
from .voice_utils.voice_validation import is_user_voice
    
class CreateUserAPI(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)
    def post(self,request,format = None):
        serializer = self.serializer_class(data = request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({
                'errors':serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        data['password'] = make_password(data['password'])
        
        audio_file_path = save_file_into_permanent_folder(data['audio_file'])
        data.pop('audio_file')
        
        user = User.objects.create(**data)
        user_voice = UserVoice.objects.create(user = user, filename = audio_file_path)
        token = AuthToken.objects.create(user)[1]
        return Response(data = {
                    'first_name' : user.first_name,
                    'last_name': user.last_name,
                    'username':user.username,
                    'email': user.email,
                    'id':user.id,
                    'user_voice_id':user_voice.id,
                    'token':token,#create and return a token here
                    'message':"User Created successfully",
                },status=status.HTTP_201_CREATED)
            
class UpdateUserAPI(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    
    
class LoginUserAPI(knoxViews.LoginView):
    # By defaulte a user must be authenticated to use an API.
    # but when ever we specify some permission classes, these classes will be applied
    permission_classes = (AllowAny,)
    serializer_class = LoginUserSerializer
    def post(self,request,format = None):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request=request,user=user)
            response = super().post(request,format=None)
        else:
            return Response({
                'errors' : serializer.errors,
                
            },status=status.HTTP_400_BAD_REQUEST)
        
        custom_response_data = {
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'id': user.id,
            'token': response.data['token'],  
        }
        
        return Response(custom_response_data, status=status.HTTP_200_OK)

class VoiceLoginUserAPI(knoxViews.LoginView):
    permission_classes = (HasRelatedUserVoice,HasRelatedUserStatement,)
    serializer_class = LoginUserVoiceSerializer
    def post(self,request,format = None):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request=request,user=user)
            response = super().post(request,format=None)
        else:
            return Response({
                'errors' : serializer.errors,
                
            },status=status.HTTP_400_BAD_REQUEST)
        
        custom_response_data = {
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'id': user.id,
            'token': response.data['token'],  
        }
        
        return Response(custom_response_data, status=status.HTTP_200_OK)

class SaveUserVoiceAPI(APIView):
    serializer_class = SaveUserVoiceSerializer
    permission_classes = (IsAuthenticated,)
    def post(self,request,format = None):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                audio_file = serializer.validated_data.get('audio_file')
                file_path = save_file_into_permanent_folder(audio_file)
                userVoice = UserVoice(filename = file_path, user = request.user)
                
                #delete the old user voice
                oldUserVoice = UserVoice.objects.filter(user = request.user).first()
                try:
                    os.remove(oldUserVoice.filename)
                except FileNotFoundError:
                    #already deleted
                    pass
                oldUserVoice.delete()
                
                userVoice.save()
                return Response({
                    'message':'Voice saved successfully'
                },status=status.HTTP_201_CREATED)
            except Exception as ex:
                print(ex)
                return Response({
                    'message':'an error occurred!'
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'message':'invalid audio file'
            },status=status.HTTP_400_BAD_REQUEST)


class GetRandomSatementAPI(APIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        sentence = generate_random_arabic_sentence(min_words=30,max_words=50)
        return Response({
            'message':'text generated successfully',
            'data':sentence
        },status=status.HTTP_200_OK)
        

        
class GetRandomStatementLoginAPI(APIView):
    permission_classes = (HasRelatedUserVoice,)
    serializer_class = GetRandomTextSerializer
    def post(self,request,format = None):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid(raise_exception=True):
            return Response({
                'message':'invalid data',
                'errors':serializer.errors,
            },status=status.HTTP_400_BAD_REQUEST)
        identifier = serializer.validated_data['identifier']
        sentence = generate_random_arabic_sentence()
        user = User.objects.filter(email = identifier.lower().strip()).get() if User.objects.filter(email = identifier.lower().strip()).exists()\
            else User.objects.filter(username = identifier).get()    
        UserStatement.objects.filter(user = user).delete()
        data = UserStatement(words = sentence, user = user)
        data.save()
        return Response({
            'message':'text generated successfully',
            'data':sentence
        },status=status.HTTP_201_CREATED)
            

class CreateCallAPI(APIView):
    permission_classes = (IsAuthenticated,CanCreateCallsPermission)
    serializer_class = CreateCallSerializer
    def post(self,request,format = None):
        serializer = self.serializer_class(data = request.data,context = {'request': request})
        if serializer.is_valid(raise_exception=True):
            identifier = serializer.validated_data.get("identifier")
            recipient=get_user_via_identifier(identifier)
            call = Call.objects.create(
                caller=request.user,
                recipient=recipient,
                status=CallStatus.CREATED.value
            )
            return Response({
                "message":"call created successfully",
                "caller": request.user.id,
                "recipient":recipient.id,
                "call_id":call.id
            },status=status.HTTP_201_CREATED)
        else:
            return Response({
                'errors' : serializer.errors,
                
            },status=status.HTTP_400_BAD_REQUEST)
    
    
class CallUpdateView(APIView):
    permission_classes = (IsAuthenticated,HasActiveOrCreatedCallsPermission)
    def patch(self, request, pk):
        try:
            call = Call.objects.get(pk=pk)
        except Call.DoesNotExist:
            return Response({
                "error":"No such call"
                },status=status.HTTP_404_NOT_FOUND)
        
        serializer = CallSerializer(call, data=request.data, partial=True,context = {'request':request})
        if serializer.is_valid():
            serializer.save(status=CallStatus.CLOSED.value)  # Assuming CallStatus is imported
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CallCheckView(APIView):
    permission_classes = (IsAuthenticated,IsCallerOrRecipient)
    def get_object(self):
        call_id = self.kwargs['pk']
        call =  get_object_or_404(Call, pk=call_id)
        self.check_object_permissions(self.request, call)
        return call
    def patch(self, request, pk):
        call = self.get_object()
        serializer = CallCheckSerializer(call,data = request.data, partial = True, context = {'request': request})
        
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            audio_file = data.get('audio_file')
            user = request.user
            if is_deep_fake_audio(audio_file) or (not is_user_voice(user,audio_file)):
                file_path = save_file_into_permanent_folder(audio_file)
                DeepAudioArchive.objects.create(user = request.user, filename = file_path, call = call)        
                
                if call.caller.pk == request.user.pk:
                    call.caller_status = FakeStatus.FAKE.value
                else:
                    call.recipient_status = FakeStatus.FAKE.value
                call.save()
            call_status = {
                "caller_status" : get_fake_status_name(call.caller_status),
                "recipient_status":get_fake_status_name(call.recipient_status),
            }
            if call.caller.pk == request.user.pk:
                call_status['caller_status'] = FakeStatus.REAL.name
            else:
                call_status['recipient_status'] = FakeStatus.FAKE.name

            return Response({
                "message":"updated successfully",
                "caller_status":call_status['caller_status'],
                'recipient_status':call_status['recipient_status']
                },status=status.HTTP_200_OK)
        else:
            return Response({
                "error":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
        
        

class AcceptDeclineIncomingCalles(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format = None):
        serializer = AcceptDeclineIncomingCallsSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({
                "error":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        calls =  Call.objects.filter(recipient = user,status = CallStatus.CREATED.value)
        call:Call = None
        if calls:
            call = calls.first()
        else:
            return Response({
                "error":"No Incoming calles to be accepted or declined!"
            },status=status.HTTP_400_BAD_REQUEST)
        
        #accept or decline the call
        accept = serializer.validated_data.get("accept")
        call_status = CallStatus.CREATED.name
        if accept:
            call.status = CallStatus.RUNNING.value
            call_status = CallStatus.RUNNING.name
        else:
            call.status = CallStatus.CLOSED.value
            call_status = CallStatus.CLOSED.name
        call.save()
        
        return Response({
        "call_id":call.pk,
        "call_status":call_status,
        "call_status_id":call.status,
        "message":"status changed successfully"
        },status=status.HTTP_200_OK)
        
class IsDeepFakeAudioAPI(APIView):
    permission_classes = (AllowAny,)
    serializer_class = IsDeepFakeAPISerializer
    def post(self,request,format = None):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid(raise_exception=True):
            return Response({
                "error":serializer.errors,
            },status=status.HTTP_400_BAD_REQUEST)
        audio_file = serializer.validated_data.get("audio_file")
        
        return Response({
            "message":"this is a deepfake voice" if is_deep_fake_audio(audio_file) else "this is a real voice"
        },status=status.HTTP_200_OK)