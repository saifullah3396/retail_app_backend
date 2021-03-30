"""
Defines the serializers used in the DeepstreamServers api.
"""


from ..models import DeepstreamServer


class DeepstreamServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'ip_addr', 'block', 'camera')
