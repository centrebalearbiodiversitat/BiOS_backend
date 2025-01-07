from rest_framework import serializers

from apps.tags.models import Directive, IUCNData, TaxonTag, Habitat, Tag, System
from apps.versioning.serializers import OriginIdSerializer
from common.utils.serializers import BaseSerializer, CaseModelSerializer


class DirectiveSerializer(CaseModelSerializer):
	sources = OriginIdSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = Directive
		exclude = ("id", "taxonomy", "batch")


class HabitatSerializer(CaseModelSerializer):
	sources = OriginIdSerializer(many=True)

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
	sources = OriginIdSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = TaxonTag
		exclude = ("id", "taxonomy", "batch")


class SystemSerializer(CaseModelSerializer):
	sources = OriginIdSerializer(many=True)

	class Meta:
		model = System
		fields = ["freshwater", "marine", "terrestrial", "sources"]


class IUCNDataSerializer(CaseModelSerializer):
	iucn_global = serializers.CharField(source="get_iucn_global_display")
	iucn_europe = serializers.CharField(source="get_iucn_europe_display")
	iucn_mediterranean = serializers.CharField(source="get_iucn_mediterranean_display")
	sources = OriginIdSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = IUCNData
		exclude = ("id", "taxonomy", "batch", "habitats")
