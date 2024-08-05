from rest_framework import serializers

from apps.taxonomy.models import Authorship, TaxonData, TaxonomicLevel, Habitat
from apps.versioning.serializers import OriginSourceSerializer
from common.utils.serializers import CaseModelSerializer


class BaseTaxonomicLevelSerializer(CaseModelSerializer):
	scientific_name_authorship = serializers.CharField(source="verbatim_authorship")
	taxon_rank = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()
	accepted_modifier = serializers.SerializerMethodField()
	images = OriginSourceSerializer(many=True)

	def get_accepted_modifier(self, obj):
		return obj.readable_accepted_modifier()

	def get_name(self, obj):
		return str(obj)

	def get_taxon_rank(self, obj):
		return obj.readable_rank()

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "name", "taxon_rank", "scientific_name_authorship", "accepted", "accepted_modifier", "images"]


class SearchTaxonomicLevelSerializer(CaseModelSerializer):
	scientific_name_authorship = serializers.CharField(source="verbatim_authorship")
	taxon_rank = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()
	accepted_modifier = serializers.SerializerMethodField()
	# images = OriginSourceSerializer(many=True)

	def get_accepted_modifier(self, obj):
		return obj.readable_accepted_modifier()

	def get_name(self, obj):
		return str(obj)

	def get_taxon_rank(self, obj):
		return obj.readable_rank()

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "name", "taxon_rank", "scientific_name_authorship", "accepted", "accepted_modifier"]


class TaxonCompositionSerializer(BaseTaxonomicLevelSerializer):
	total_species = serializers.IntegerField()

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "name", "rank", "total_species"]


class AuthorshipSerializer(serializers.ModelSerializer):
	class Meta:
		model = Authorship
		fields = ["id", "name", "accepted"]


class HabitatSerializer(serializers.ModelSerializer):
	class Meta:
		model = Habitat
		fields = ["id", "name"]


class BaseTaxonDataSerializer(CaseModelSerializer):
	iucn_global = serializers.SerializerMethodField()
	iucn_europe = serializers.SerializerMethodField()
	iucn_mediterranean = serializers.SerializerMethodField()
	habitat = HabitatSerializer(many=True)

	def get_iucn_global(self, obj):
		return obj.get_iucn_global_display()

	def get_iucn_europe(self, obj):
		return obj.get_iucn_europe_display()

	def get_iucn_mediterranean(self, obj):
		return obj.get_iucn_mediterranean_display()

	class Meta:
		model = TaxonData
		# exclude = ["taxonomy"]


class TaxonDataSerializer(BaseTaxonDataSerializer):
	class Meta:
		exclude = ["taxonomy"]
