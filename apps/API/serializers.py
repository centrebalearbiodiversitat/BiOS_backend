from rest_framework import serializers


class APIStatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=128)
    version = serializers.CharField(max_length=128)
    email = serializers.CharField(max_length=128)
