from rest_framework import serializers

from apps.tags.models import TaxonTag, Habitat, Tag, System, IUCNData
from apps.versioning.serializers import OriginSourceSerializer


class HabitatSerializer(serializers.ModelSerializer):
	sources = OriginSourceSerializer(many=True)

	class Meta:
		model = Habitat
		fields = ["sources", "name"]


class TagSerializer(serializers.ModelSerializer):
	tag_type = serializers.SerializerMethodField()

	def get_tag_type(self, obj):
		return Tag.TRANSLATE_TYPE[obj.tag_type]

	class Meta:
		model = Tag
		fields = ["name", "tag_type"]


class TaxonTagSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = TaxonTag
        fields = '__all__'


class SystemSerializer(serializers.ModelSerializer):
	sources = OriginSourceSerializer(many=True)
	class Meta:
		model = System
		fields = "__all__"


class IUCNDataSerializer(serializers.ModelSerializer):
    iucn_global = serializers.CharField(source='get_iucn_global_display')
    iucn_europe = serializers.CharField(source='get_iucn_europe_display')
    iucn_mediterranean = serializers.CharField(source='get_iucn_mediterranean_display')
    habitat = serializers.SlugRelatedField(
        many=True, 
        slug_field='name', 
        queryset=Habitat.objects.all()
    )

    class Meta:
        model = IUCNData
        fields = '__all__'