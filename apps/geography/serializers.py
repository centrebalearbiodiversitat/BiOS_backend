from rest_framework import serializers
from common.utils.serializers import CaseModelSerializer
from apps.geography.models import GeographicLevel
from django.core.serializers import serialize


class GeographicLevelSerializer(CaseModelSerializer):
	decimal_latitude = serializers.DecimalField(source="location.y", max_digits=8, decimal_places=5, allow_null=True)
	decimal_longitude = serializers.DecimalField(source="location.x", max_digits=8, decimal_places=5, allow_null=True)
	rank = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()
	area = serializers.SerializerMethodField()

	def get_rank(self, obj):
		return obj.get_readable_rank()

	def get_name(self, obj):
		return str(obj)

	def get_area(self, obj):
		return serialize("geojson", [obj], geometry_field="area", fields=[])

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
			"area",
		]
