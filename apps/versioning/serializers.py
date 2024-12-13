from rest_framework import serializers
from apps.versioning.models import Basis, Source, OriginId
from common.utils.serializers import CaseModelSerializer


class SourceSerializer(CaseModelSerializer):
	source_type = serializers.CharField(source='get_source_type_display')
	extraction_method = serializers.CharField(source='get_extraction_method_display')
	data_type = serializers.CharField(source='get_data_type_display')
	name = serializers.CharField(source='basis.internal_name')

	
	class Meta:
		model = Source
		fields = [
			"id",
			"source_type",
			"extraction_method",
			"data_type",
			"url",
			"name",
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
		fields = "__all__"
