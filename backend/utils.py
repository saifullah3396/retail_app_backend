
from rest_framework import exceptions


def get_request_user(serializer, raise_exception=False):
    # get user requesting for a new registration
    request_user = None
    request = serializer.context.get("request")
    if request and hasattr(request, "user"):
        request_user = request.user
    else:
        if raise_exception:
            # raise unauthorized error if user is not found
            # most probably this will never get called
            raise exceptions.PermissionDenied()
    return request_user
