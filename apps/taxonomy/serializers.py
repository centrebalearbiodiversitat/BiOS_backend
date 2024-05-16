from rest_framework import serializers
from apps.taxonomy.models import TaxonomicLevel, Authorship


class BaseTaxonomicLevelSerializer(serializers.ModelSerializer):
	scientific_name_authorship = serializers.CharField(source="verbatim_authorship")
	taxon_rank = serializers.SerializerMethodField()

	def get_taxon_rank(self, obj):
		return obj.readable_rank()

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "name", "taxon_rank", "scientific_name_authorship"]
