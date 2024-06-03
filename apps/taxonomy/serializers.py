from apps.taxonomy.models import TaxonomicLevel, Authorship
from common.utils.serializers import CaseModelSerializer
from rest_framework import serializers


class BaseTaxonomicLevelSerializer(CaseModelSerializer):
	scientific_name_authorship = serializers.CharField(source="verbatim_authorship")
	taxon_rank = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()
	accepted_modifier = serializers.SerializerMethodField()

	def get_accepted_modifier(self, obj):
		return obj.readable_accepted_modifier()

	def get_name(self, obj):
		return str(obj)

	def get_taxon_rank(self, obj):
		return obj.readable_rank()

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "name", "taxon_rank", "scientific_name_authorship", "accepted", "accepted_modifier"]


class AuthorshipSerializer(serializers.ModelSerializer):
	class Meta:
		model = Authorship
		fields = ["id", "name", "accepted"]
