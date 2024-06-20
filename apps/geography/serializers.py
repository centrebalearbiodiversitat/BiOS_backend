from rest_framework import serializers
from common.utils.serializers import CaseModelSerializer
from apps.geography.models import GeographicLevel


class GeographicLevelSerializer(CaseModelSerializer):
	rank = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()

	def get_rank(self, obj):
		return obj.get_readable_rank()

	def get_name(self, obj):
		return str(obj)

	class Meta:
		model = GeographicLevel
		fields = [
			"id",
			"parent",
			"name",
			"rank",
			"decimal_latitude",
			"decimal_longitude",
			"coordinate_uncertainty_in_meters",
			"elevation",
			"depth",
		]
