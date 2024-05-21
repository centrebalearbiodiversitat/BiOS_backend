from rest_framework import serializers

from apps.geography.models import GeographicLevel


class GeographicLevelSerializer(serializers.ModelSerializer):
	rank = serializers.SerializerMethodField()

	def get_rank(self, obj):
		return obj.get_readable_rank()

	class Meta:
		model = GeographicLevel
		fields = [
			"id",
			"name",
			"rank",
			"decimal_latitude",
			"decimal_longitude",
			"coordinate_uncertainty_in_meters",
			"elevation",
			"depth",
		]
