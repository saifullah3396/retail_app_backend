"""
Defines the serializers used in the DeepstreamServers api.
"""

from django.db import IntegrityError
from rest_framework import serializers

from deepstream_servers.models import (DeepstreamDiagnostics,
                                       DeepstreamLogEntry, DeepstreamServer)


# pylint: disable=missing-class-docstring
class DeepstreamServerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeepstreamServer
        fields = ('id', 'ip_addr', 'mac_addr', 'block')


class DeepstreamServerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeepstreamServer
        fields = ('ip_addr', 'mac_addr', 'block')
        extra_kwargs = {
            'ip_addr': {'required': True},
            'mac_addr': {'required': True},
            'block': {'required': True},
        }

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class LogEntryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeepstreamLogEntry
        fields = ('id', 'message', 'received_at', 'deepstream_server')


class DiagnosticsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeepstreamDiagnostics
        fields = (
            'id', 'deepstream_server', 'cpu_utilization',
            'gpu_utilization', 'memory_usage',
            'gpu_memory_usage', 'temperature', 'received_at')


class DeepstreamServerDetailSerializer(serializers.ModelSerializer):
    log_entries = serializers.SerializerMethodField()
    diagnostics = serializers.SerializerMethodField()

    def get_log_entries(self, server):
        """
        Returns the log entries of server.
        """
        log_entries = DeepstreamLogEntry.objects.filter(
            deepstream_server__id=server.id)
        return \
            LogEntryDetailSerializer(
                log_entries, many=True, context=self.context).data

    def get_diagnostics(self, server):
        """
        Returns the diagnostics of server.
        """
        diagnostics = DeepstreamDiagnostics.objects.filter(
            deepstream_server__id=server.id)
        return \
            DiagnosticsDetailSerializer(
                diagnostics, many=True, context=self.context).data

    class Meta:
        model = DeepstreamServer
        fields = (
            'id',
            'ip_addr',
            'mac_addr',
            'status',
            'connected_at',
            'last_echo_at',
            'block',
            'log_entries',
            'diagnostics')


class DeepstreamServerUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeepstreamServer
        fields = ('ip_addr', 'mac_addr', 'block')

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
