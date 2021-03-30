"""
Defines the serializers used in the Servers api.
"""


from ..models import Server


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'ip_addr', 'block', 'camera')
