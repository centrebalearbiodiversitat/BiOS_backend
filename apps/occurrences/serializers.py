from rest_framework import serializers
from common.utils.serializers import CaseModelSerializer
from ..geography.models import GeographicLevel
from .models import Occurrence


class OccurrenceSerializer(CaseModelSerializer):
	location = serializers.PrimaryKeyRelatedField(queryset=GeographicLevel.objects.all(), source="geographical_location")


	class Meta:
		model = Occurrence
		fields = (
			"id",
			"basis_of_record",
			"coordinate_uncertainty_in_meters",
			"decimal_latitude",
			"decimal_longitude",
			# "day",
			"depth",
			"elevation",
			# "event_date",
			# "location",
			# "month",
			"taxonomy",
			# "voucher",
			# "year",
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
		elif year:
			return f"{year}"
		else:
			return None


class OccurrenceSerializer(BaseOccurrenceSerializer):
	basis_of_record = serializers.SerializerMethodField()

	event_date = serializers.SerializerMethodField()
	day = serializers.IntegerField(source="collection_date_day")
	month = serializers.IntegerField(source="collection_date_month")
	year = serializers.IntegerField(source="collection_date_year")

	location = GeographicLevelSerializer(source="geographical_location")
	taxonomy = BaseTaxonomicLevelSerializer()
	sources = OriginSourceSerializer(many=True)

	class Meta:
		model = Occurrence
		fields = (
			"id",
			"basis_of_record",
			"coordinate_uncertainty_in_meters",
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
			"sources",
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
		elif year:
			return f"{year}"
		else:
			return None
