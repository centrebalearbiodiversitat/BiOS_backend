from rest_framework import serializers

from apps.tags.models import Directive, IUCNData, TaxonTag, Habitat, Tag, System
from apps.versioning.serializers import OriginIdSerializer, OriginIdMinimalSerializer
from common.utils.serializers import BaseSerializer, CaseModelSerializer


class DirectiveSerializer(CaseModelSerializer):
	sources = OriginIdMinimalSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = Directive
		exclude = ("id", "taxonomy", "batch")


class HabitatSerializer(CaseModelSerializer):
	sources = OriginIdMinimalSerializer(many=True)

	class Meta:
		model = Habitat
		fields = ["id", "name", "sources"]


class TagSerializer(CaseModelSerializer):
	tag_type = serializers.SerializerMethodField()

	def get_tag_type(self, obj):
		return obj.translate_tag_type()

	class Meta:
		model = Tag
		fields = "__all__"


class TaxonTagSerializer(CaseModelSerializer):
	tag = TagSerializer()
	sources = OriginIdMinimalSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = TaxonTag
		exclude = ("id", "taxonomy", "batch")


class SystemSerializer(CaseModelSerializer):
	sources = OriginIdMinimalSerializer(many=True)

	class Meta:
		model = System
		fields = ["freshwater", "marine", "terrestrial", "sources"]


class IUCNDataSerializer(CaseModelSerializer):
	assessment = serializers.CharField(source="get_assessment_display")
	region = serializers.CharField(source="get_region_display")
	sources = OriginIdMinimalSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = IUCNData
		exclude = ("id", "taxonomy", "batch")
