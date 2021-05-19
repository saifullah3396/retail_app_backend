"""
Defines the serializers used in user REST api views.
"""
# pylint: disable=missing-class-docstring

from django.db.utils import IntegrityError
from rest_framework import serializers

from user_auth.models import UserGroup
from users.models import AppUser


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGroup
        fields = ['name', 'authority']


class AppUserListSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = AppUser
        fields = [
            'id',
            'username',
            'email',
            'is_superuser',
            'groups']


class AppUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = []

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class AppUserRetrieveSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = AppUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_superuser',
            'groups',
            'avatar']


class AppUserUpdateSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = AppUser
        fields = [
            'id',
            'username',
            'email',
            'is_superuser',
            'first_name',
            'last_name',
            'groups',
            'avatar']
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'read_only': True},
            'is_superuser': {'read_only': True},
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
