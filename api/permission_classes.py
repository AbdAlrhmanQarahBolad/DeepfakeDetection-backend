from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User
from .models import Call, CallStatus
from django.core.exceptions import PermissionDenied
from django.db.models import Q



class HasRelatedUserStatement(BasePermission):
    """
    Custom permission to only allow users with a related UserStatement record.
    """

    def has_permission(self, request, view):
        # Extract the identifier (email or username) from the request data
        identifier = request.data.get('identifier')

        # Check if the identifier is provided
        if not identifier:
            raise PermissionDenied("Identifier is required.")

        try:
            # Attempt to retrieve the user by email
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            # Try retrieving the user by username
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                raise PermissionDenied("User not found.")

        # If the user is found, check if they have a related UserStatement record
        try:
            if user and user.statement:
                return True
            else:
                raise PermissionDenied("User does not have a related statement.")
        except Exception as ex:
            raise PermissionDenied("User does not have a related statement.")


from django.core.exceptions import PermissionDenied

class HasRelatedUserVoice(BasePermission):
    
    def has_permission(self, request, view):
        # Extract the identifier (email or username) from the request data
        identifier = request.data.get('identifier')

        # Check if the identifier is provided
        if not identifier:
            raise PermissionDenied("Identifier is required.")

        try:
            # Attempt to retrieve the user by email
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            # Try retrieving the user by username
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                raise PermissionDenied("User not found.")

        # If the user is found, check if they have a related UserVoice record
        if user and user.voice:
            return True
        else:
            raise PermissionDenied("User does not have a related voice.")


def hasActiveOrCreatedCalls(user)->bool:
    # Check if the user has any calls that are either 'created' or 'running'
        user_calls = Call.objects.filter(Q(caller=user) | Q(recipient=user),
                                         status__in=[CallStatus.CREATED.value, CallStatus.RUNNING.value])
        return user_calls.exists()
        



#needed for closing a call
class HasActiveOrCreatedCallsPermission(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has any calls that are either 'created' or 'running'
        
        if not hasActiveOrCreatedCalls(request.user):
            # If the user does not have any active or created calls, raise a PermissionDenied exception
            # with a custom message
            msg = "You do not have active or created calls."
            raise PermissionDenied(msg)
        return True

#needed for creating a new call
class CanCreateCallsPermission(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has any calls that are either 'created' or 'running'
        
        if hasActiveOrCreatedCalls(request.user):
            # If the user does not have any active or created calls, raise a PermissionDenied exception
            # with a custom message
            msg = "You already have active or created calls."
            raise PermissionDenied(msg)
        
        return True

class CanAcceptCallPermission(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has any calls that are 'created' and they are the recipient
        user_has_created_call = Call.objects.filter(
            Q(status=CallStatus.CREATED.value) &
            Q(recipient=request.user)
        ).exists()
        
        if not user_has_created_call:
            msg = "You don't have created calles."
            raise PermissionDenied(msg)
        return True
    
    

class IsCallerOrRecipient(BasePermission):
    """
    Custom permission class to allow access only to the caller or recipient of a call.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is the caller or recipient of the call
        if request.user == obj.caller or request.user == obj.recipient:
            return True
        else:
            msg = "You are not allowed to access this call info."
            raise PermissionDenied(msg)

