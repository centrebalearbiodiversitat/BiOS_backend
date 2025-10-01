from rest_framework import serializers
from common.utils.serializers import CaseModelSerializer
from apps.geography.models import GeographicLevel
from django.core.serializers import serialize


class MinimalGeographicLevelSerializer(CaseModelSerializer):
	rank = serializers.CharField(source="get_readable_rank", default=None)
	name = serializers.CharField(default=None)

	def get_rank(self, obj):
		return None if obj is None else obj.get_readable_rank()

	class Meta:
		model = GeographicLevel
		fields = ["id", "parent", "name", "rank"]


class GeographicLevelSerializer(MinimalGeographicLevelSerializer):
	decimal_latitude = serializers.DecimalField(source="location.y", max_digits=8, decimal_places=5, allow_null=True)
	decimal_longitude = serializers.DecimalField(source="location.x", max_digits=8, decimal_places=5, allow_null=True)
	area = serializers.SerializerMethodField()

	def get_area(self, obj):
		return serialize("geojson", [obj], geometry_field="area", fields=[])

	class Meta:
		model = GeographicLevel
		fields = MinimalGeographicLevelSerializer.Meta.fields + [
			"decimal_latitude",
			"decimal_longitude",
			"coordinate_uncertainty_in_meters",
			"area",
		]
