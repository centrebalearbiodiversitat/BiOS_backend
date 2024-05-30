from rest_framework import serializers
from common.utils.models import SynonymModel
from apps.versioning.models import Source, Batch, OriginSource


class SourceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Source
		fields = "__all__"


class OriginSourceSerializer(serializers.ModelSerializer):

	class Meta:
		model = OriginSource
		fields = "__all__"
