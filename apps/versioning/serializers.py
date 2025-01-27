from rest_framework import serializers
from apps.versioning.models import Basis, Source, OriginId
from common.utils.serializers import CaseModelSerializer


class BasisSerializer(CaseModelSerializer):
	class Meta:
		model = Basis
		fields = "__all__"


class SourceSerializer(CaseModelSerializer):
	id = serializers.CharField(source="basis.id")
	name = serializers.SerializerMethodField()
	source_type = serializers.CharField(source="get_source_type_display")
	extraction_method = serializers.CharField(source="get_extraction_method_display")
	data_type = serializers.CharField(source="get_data_type_display")

	def get_name(self, obj):
		return obj.basis.acronym or obj.basis.name or obj.basis.internal_name

	class Meta:
		model = Source
		fields = [
			"id",
			"name",
			"data_type",
			"source_type",
			"extraction_method",
			"url",
		]


class SourceCountSerializer(SourceSerializer):
	count = serializers.IntegerField()

	class Meta(SourceSerializer.Meta):
		fields = "count"


class OriginIdSerializer(CaseModelSerializer):
	source = SourceSerializer(read_only=True)

	class Meta:
		model = OriginId
		exclude = ("id",)
