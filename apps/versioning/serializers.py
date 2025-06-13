from rest_framework import serializers
from apps.versioning.models import Basis, Source, OriginId
from common.utils.serializers import CaseModelSerializer


class BasisSerializer(CaseModelSerializer):
	name = serializers.SerializerMethodField()

	def get_name(self, obj):
		return obj.get_name()

	class Meta:
		model = Basis
		fields = [
			"name",
			"acronym",
			"url",
			"description",
			"authors",
			"citation",
			"contact"
		]


class SourceSerializer(CaseModelSerializer):
	# id = serializers.CharField(source="basis.id")
	name = serializers.SerializerMethodField()
	source_type = serializers.CharField(source="get_source_type_display")
	extraction_method = serializers.CharField(source="get_extraction_method_display")
	data_type = serializers.CharField(source="get_data_type_display")

	def get_name(self, obj):
		return obj.basis.get_name()

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
		fields = SourceSerializer.Meta.fields + ["count"]


class OriginIdSerializer(CaseModelSerializer):
	source = SourceSerializer(read_only=True)

	class Meta:
		model = OriginId
		exclude = ("id",)


class SourceMinimalSerializer(CaseModelSerializer):
	name = serializers.SerializerMethodField()

	def get_name(self, obj):
		return obj.basis.get_name()

	class Meta:
		model = Source
		fields = ["id", "name"]


class OriginIdMinimalSerializer(CaseModelSerializer):
	source = SourceMinimalSerializer(read_only=True)

	class Meta:
		model = OriginId
		exclude = ("id",)
