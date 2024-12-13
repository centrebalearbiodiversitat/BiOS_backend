from rest_framework import serializers

from apps.tags.models import (
	Directive,
	IUCNData,
	TaxonTag,
	Habitat,
	Tag,
	System
)
from apps.versioning.serializers import OriginIdSerializer
from common.utils.serializers import BaseSerializer, CaseModelSerializer


class DirectiveSerializer(CaseModelSerializer):
	sources = OriginIdSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = Directive

class HabitatSerializer(CaseModelSerializer):
	sources = OriginIdSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = Habitat


class TagSerializer(CaseModelSerializer):
	tag_type = serializers.SerializerMethodField()

	def get_tag_type(self, obj):
		return Tag.TRANSLATE_TYPE[obj.tag_type]

	class Meta(BaseSerializer.Meta):
		model = Tag


class TaxonTagSerializer(CaseModelSerializer):
	tags = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Tag.objects.all())
	sources = OriginIdSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = TaxonTag


class SystemSerializer(CaseModelSerializer):
	sources = OriginIdSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = System


class IUCNDataSerializer(CaseModelSerializer):
	habitat = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Habitat.objects.all())
	iucn_global = serializers.CharField(source="get_iucn_global_display")
	iucn_europe = serializers.CharField(source="get_iucn_europe_display")
	iucn_mediterranean = serializers.CharField(source="get_iucn_mediterranean_display")
	sources = OriginIdSerializer(many=True)

	class Meta(BaseSerializer.Meta):
		model = IUCNData
