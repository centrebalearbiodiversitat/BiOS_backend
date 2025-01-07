from rest_framework import serializers
from apps.versioning.models import Basis, Source, OriginId
from common.utils.serializers import CaseModelSerializer


class SourceSerializer(CaseModelSerializer):
	id = serializers.CharField(source="basis.id")
	name = serializers.CharField(source="basis.internal_name")
	source_type = serializers.CharField(source="get_source_type_display")
	extraction_method = serializers.CharField(source="get_extraction_method_display")
	data_type = serializers.CharField(source="get_data_type_display")

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


class BasisSerializer(CaseModelSerializer):
	class Meta:
		model = Basis
		fields = "__all__"


class SourceCountSerializer(SourceSerializer):
	count = serializers.IntegerField()

	class Meta(SourceSerializer.Meta):
		fields = SourceSerializer.Meta.fields + ["count"]


class OriginIdSerializer(CaseModelSerializer):
	source = SourceSerializer(read_only=True)

	class Meta:
		model = OriginId
		exclude = ("id",)
