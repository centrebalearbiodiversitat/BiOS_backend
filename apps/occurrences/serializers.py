from rest_framework import serializers
from .models import Occurrence
from common.utils.serializers import CaseModelSerializer


class OccurrenceSerializer(CaseModelSerializer):
	basis_of_record = serializers.SerializerMethodField()
	coordinatesUncertaintyInMeters = serializers.IntegerField(source="coordinatesUncertaintyMeters")
	day = serializers.IntegerField(source="collection_date_day")
	decimal_latitude = serializers.DecimalField(source="latitude", max_digits=8, decimal_places=5)
	decimal_longitude = serializers.DecimalField(source="longitude", max_digits=8, decimal_places=5)
	depth = serializers.IntegerField(source="depthMeters")
	elevation = serializers.IntegerField(source="elevationMeters")
	event_date = serializers.SerializerMethodField()
	location = serializers.CharField(source="geographical_location")
	month = serializers.IntegerField(source="collection_date_month")
	year = serializers.IntegerField(source="collection_date_year")

	class Meta:
		model = Occurrence
		fields = (
			"basis_of_record",
			"coordinatesUncertaintyInMeters",
			"decimal_latitude",
			"decimal_longitude",
			"day",
			"depth",
			"elevation",
			"event_date",
			"location",
			"month",
			"taxonomy",
			"voucher",
			"year",
		)

	def get_basis_of_record(self, obj):
		return Occurrence.TRANSLATE_BASIS_OF_RECORD[obj.basis_of_record]

	def get_event_date(self, obj):
		year = obj.collection_date_year
		month = obj.collection_date_month
		day = obj.collection_date_day

		if year and month and day:
			return f"{year}-{month:02}-{day:02}"
		elif year and month:
			return f"{year}-{month:02}"
		elif year and day:
			return f"{year}"
		else:
			return None
