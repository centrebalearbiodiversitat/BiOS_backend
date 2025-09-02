from rest_framework import serializers

from apps.taxonomy.models import Authorship, TaxonomicLevel
from apps.tags.serializers import (
	IUCNDataSerializer,
	TaxonTagSerializer,
)
from apps.versioning.serializers import OriginIdSerializer
from common.utils.serializers import CaseModelSerializer


class MinimalTaxonomicLevelSerializer(CaseModelSerializer):
	taxon_rank = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()

	def get_name(self, obj):
		return str(obj)

	def get_taxon_rank(self, obj):
		return obj.readable_rank()

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "name", "taxon_rank"]


class BaseTaxonomicLevelSerializer(CaseModelSerializer):
	scientific_name_authorship = serializers.CharField(source="verbatim_authorship")
	taxon_rank = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()
	accepted_modifier = serializers.SerializerMethodField()
	images = OriginIdSerializer(many=True)
	parent = serializers.SerializerMethodField()

	def get_accepted_modifier(self, obj):
		return obj.readable_accepted_modifier()

	def get_name(self, obj):
		return str(obj)

	def get_taxon_rank(self, obj):
		return obj.readable_rank()

	def get_parent(self, obj):
		try:
			return obj.parent.id
		except:
			return None

	class Meta:
		model = TaxonomicLevel
		fields = [
			"id",
			"name",
			"taxon_rank",
			"scientific_name_authorship",
			"accepted",
			"accepted_modifier",
			"images",
			"parent",
		]


class AncestorsTaxonomicLevelSerializer(BaseTaxonomicLevelSerializer):
	ancestors = serializers.SerializerMethodField()

	def get_ancestors(self, obj):
		return MinimalTaxonomicLevelSerializer(obj.get_ancestors(), many=True).data

	class Meta(BaseTaxonomicLevelSerializer.Meta):
		fields = BaseTaxonomicLevelSerializer.Meta.fields + [
			"ancestors"
		]


class SearchTaxonomicLevelSerializer(CaseModelSerializer):
	scientific_name_authorship = serializers.CharField(source="verbatim_authorship")
	taxon_rank = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()
	accepted_modifier = serializers.SerializerMethodField()
	# images = OriginIdSerializer(many=True)

	def get_accepted_modifier(self, obj):
		return obj.readable_accepted_modifier()

	def get_name(self, obj):
		return str(obj)

	def get_taxon_rank(self, obj):
		return obj.readable_rank()

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "name", "taxon_rank", "scientific_name_authorship", "accepted", "accepted_modifier"]


class TaxonomicFilterSerializer(AncestorsTaxonomicLevelSerializer):
	iucndata = IUCNDataSerializer(source="iucndata_set", many=True, read_only=True)
	tag = TaxonTagSerializer(source="taxontag_set", many=True, read_only=True)

	class Meta(AncestorsTaxonomicLevelSerializer.Meta):
		fields = AncestorsTaxonomicLevelSerializer.Meta.fields + [
			"iucndata",
			"tag",
		]


class TaxonCompositionSerializer(BaseTaxonomicLevelSerializer):
	total_species = serializers.IntegerField()

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "name", "rank", "total_species"]


class AuthorshipSerializer(serializers.ModelSerializer):
	class Meta:
		model = Authorship
		fields = ["id", "name", "accepted"]
