"""
Defines the serializers used in the DSServers api.
"""

from django.db import IntegrityError
from rest_framework import serializers

from ds_servers.models import DSDiagnostics, DSLogEntry, DSServer


# pylint: disable=missing-class-docstring
class DSServerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSServer
        fields = ('id', 'ip_addr')


class DSServerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSServer
        fields = ('id', 'ip_addr')
        extra_kwargs = {
            'ip_addr': {'required': True}
        }

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class LogEntryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DSLogEntry
        fields = ('id', 'message', 'received_at', 'ds_server')


class DiagnosticsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DSDiagnostics
        fields = (
            'id', 'ds_server', 'cpu_utilization',
            'gpu_utilization', 'memory_usage',
            'gpu_memory_usage', 'temperature', 'received_at')


class DSServerRetrieveSerializer(serializers.ModelSerializer):
    log_entries = serializers.SerializerMethodField()
    diagnostics = serializers.SerializerMethodField()

    def get_log_entries(self, server):
        """
        Returns the log entries of server.
        """
        log_entries = DSLogEntry.objects.filter(
            ds_server__id=server.id)
        return \
            LogEntryDetailSerializer(
                log_entries, many=True, context=self.context).data

    def get_diagnostics(self, server):
        """
        Returns the diagnostics of server.
        """
        diagnostics = DSDiagnostics.objects.filter(
            ds_server__id=server.id)
        return \
            DiagnosticsDetailSerializer(
                diagnostics, many=True, context=self.context).data

    class Meta:
        model = DSServer
        fields = (
            'id',
            'ip_addr',
            'status',
            'last_echo_at',
            'log_entries',
            'diagnostics')


class DSServerUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DSServer
        fields = ('id', 'ip_addr')

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
