from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from apps.versioning.models import Source, Batch, OriginSource
from common.utils.serializers import CaseModelSerializer


class SourceSerializer(CaseModelSerializer):
	origin = SerializerMethodField()
	data_type = SerializerMethodField()

	def get_origin(self, obj):
		return Source.TRANSLATE_CHOICES[obj.origin]

	def get_data_type(self, obj):
		return Source.TRANSLATE_DATA_TYPE[obj.data_type]

	class Meta:
		model = Source
		fields = [
			"id",
			"name",
			"url",
			"origin",
			"data_type",
		]


class SourceCountSerializer(SourceSerializer):
	count = serializers.IntegerField()

	class Meta(SourceSerializer.Meta):
		fields = SourceSerializer.Meta.fields + ["count"]


class OriginSourceSerializer(CaseModelSerializer):
	source = SourceSerializer(read_only=True)

	class Meta:
		model = OriginSource
		fields = "__all__"
