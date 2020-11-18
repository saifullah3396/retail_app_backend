from rest_framework import permissions, status
from rest_framework_jwt import authentication
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from ..models import AppUser
from .serializers import \
    AdminUserSerializerAdminAccess, \
    AppUserSerializerAdminAccess, \
    AppUserSerializerAppUserAccess


class AppUserListAdminAccess(ListAPIView):
    """
    Lists all app users. Can only be accessed by staff users.
    """
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializerAdminAccess
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.IsAdminUser,)
    authentication_classes = [authentication.JSONWebTokenAuthentication]


class AppUserListAppUserAccess(APIView):
    """
    Lists all app users under organization of app admin. AppAdmin corresponds
    to organization or sub_organization admins.
    """
    serializer_class = AppUserSerializerAppUserAccess
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [authentication.JSONWebTokenAuthentication]

    def send_user_list_response(self, request, user_list):
        serializer = self.serializer_class(
            user_list, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        """
        Return the users under this user, for example if this user is an
        organization admin, this get request will return all organization
        users.
        """
        try:
            user_list = AppUser.objects.filter(
                organization=request.user.organization,
                authority__lte=request.user.authority).\
                exclude(id=request.user.id)
            if user_list:
                return self.send_user_list_response(request, user_list)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except AppUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AppUserDetailAppUserAccess(APIView):
    serializer_class = AppUserSerializerAppUserAccess
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [authentication.JSONWebTokenAuthentication]

    def send_user_response(self, request, user):
        serializer = self.serializer_class(
            user, context={'request': request})
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """
        Return the user itself if <pk>=me else returns the user with
        input <pk> if the request user has authority.
        """
        if request.user.is_staff:
            self.serializer_class = AdminUserSerializerAdminAccess
        else:
            self.serializer_class = AppUserSerializerAppUserAccess

        pk = self.kwargs.get('pk')
        if pk == "me":
            return self.send_user_response(request, request.user)
        else:
            try:
                if request.user.sub_organization is None:
                    # if sub is none then its parent to sub
                    user = AppUser.objects.filter(
                        pk=pk,
                        organization=request.user.organization,
                        authority__lte=request.user.authority)
                else:
                    # if this does not work that means user > request.user
                    # so it is forbidden
                    user = AppUser.objects.filter(
                        pk=pk,
                        organization=request.user.organization,
                        sub_organization=request.user.sub_organization,
                        authority__lte=request.user.authority)
                if user:
                    return self.send_user_response(request, user[0])
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            except AppUser.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
