from rest_framework import serializers
from apps.versioning.models import Basis, Source, OriginId
from common.utils.serializers import CaseModelSerializer


class BasisSerializer(CaseModelSerializer):
	name = serializers.SerializerMethodField()
	type = serializers.CharField(source="translate_type")

	def get_name(self, obj):
		return obj.get_name()

	class Meta:
		model = Basis
		fields = [
			"id",
			"name",
			"acronym",
			"type",
			"url",
			"description",
			"authors",
			"citation",
			"contact",
			"image",
		]


class SourceSerializer(CaseModelSerializer):
	# id = serializers.CharField(source="basis.id")
	# name = serializers.SerializerMethodField()
	# source_type = serializers.CharField(source="get_source_type_display")
	extraction_method = serializers.CharField(source="get_extraction_method_display")
	data_type = serializers.CharField(source="get_data_type_display")
	basis = BasisSerializer()

	# def get_name(self, obj):
	# 	return obj.basis.acronym or obj.basis.name or obj.basis.internal_name

	class Meta:
		model = Source
		fields = [
			"id",
			# "name",
			"basis",
			"data_type",
			"extraction_method",
			"url",
		]


class SourceCountSerializer(SourceSerializer):
	extraction_method = serializers.CharField(source="get_extraction_method_display")
	data_type = serializers.CharField(source="get_data_type_display")
	count = serializers.IntegerField()

	class Meta(SourceSerializer.Meta):
		model = Source
		fields = [
			"id",
			"data_type",
			"extraction_method",
			"count",
		]


class OriginIdSerializer(CaseModelSerializer):
	source = SourceSerializer(read_only=True)

	class Meta:
		model = OriginId
		exclude = ("id",)
