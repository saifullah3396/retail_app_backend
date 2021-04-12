"""
Defines the serializers used in the DeepstreamServers api.
"""


from ..models import DeepstreamServer, DeepstreamLogEntry, DeepstreamDiagnostics


class DeepstreamServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'ip_addr', 'mac_addr', 'block', 'camera')


class LogEntryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeepstreamLogEntry
        fields = ('id', 'message', 'received_at', 'deepstream_server')

class DiagnosticsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeepstreamDiagnostics
        fields = ('id', 'deepstream_server', 'cpu_utilization', 'gpu_utilization', 'memory_usage', 'gpu_memory_usage', 'temperature', 'received_at')

class DeepstreamServerDetailSerializer(serializers.ModelSerializer):
    log_entries = serializers.SerializerMethodField()
    diagnostics = serializers.SerializerMethodField()

    def get_log_entries(self, server):
        # return all floors in this location
        log_entries = DeepstreamLogEntry.objects.filter(deepstream_server__id=server.id)
        return \
            LogEntryDetailSerializer(log_entries, many=True, context=self.context).data

    def get_diagnostics(self, server):
        # return all floors in this location
        diagnostics = DeepstreamDiagnostics.objects.filter(deepstream_server__id=server.id)
        return \
            DiagnosticsDetailSerializer(diagnostics, many=True, context=self.context).data

    class Meta:
        model = Server
        fields = ('id', 'ip_addr', 'mac_addr', 'block', 'camera', 'log_entries', 'diagnostics')
