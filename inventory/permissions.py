from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    
    NOTE: This permission is currently redundant because the ViewSet's
    get_queryset() method already filters objects by user. The permission
    would only be triggered if:
    
    1. We changed get_queryset() to return all products
    2. We implemented a custom get_object() method
    3. We added features like product sharing
    
    We're keeping this permission class for future flexibility and to make
    our security intentions explicit, even though it's not currently being
    triggered in the normal request flow.
    
    How permissions and queryset filtering work together:
    - get_queryset() determines which objects a user can see
    - has_object_permission() determines what actions they can perform
    
    In our current implementation, get_queryset() is more restrictive,
    so this permission never gets checked.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user making the request is the owner of the object
        return obj.user == request.user
