"""
Defines the serializers used in the DeepstreamServers api.
"""
from rest_framework import serializers

from deepstream_servers.models import (DeepstreamDiagnostics,
                                       DeepstreamLogEntry, DeepstreamServer)


# pylint: disable=missing-class-docstring
class DeepstreamServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeepstreamServer
        fields = ('id', 'ip_addr', 'mac_addr', 'block', 'camera')


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
        fields = ('id', 'ip_addr', 'mac_addr', 'block',
                  'camera', 'log_entries', 'diagnostics')
