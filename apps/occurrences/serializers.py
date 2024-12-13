from rest_framework import serializers
from common.utils.serializers import CaseModelSerializer
from .models import Occurrence
from ..taxonomy.serializers import BaseTaxonomicLevelSerializer
from ..versioning.serializers import OriginIdSerializer


class BaseOccurrenceSerializer(CaseModelSerializer):
	decimal_latitude = serializers.DecimalField(source="location.y", max_digits=8, decimal_places=5, allow_null=True)
	decimal_longitude = serializers.DecimalField(source="location.x", max_digits=8, decimal_places=5, allow_null=True)

	class Meta:
		model = Occurrence
		fields = (
			"id",
			# "basis_of_record",
			"coordinate_uncertainty_in_meters",
			"decimal_latitude",
			"decimal_longitude",
			# "coords",
			# "day",
			# "depth",
			# "elevation",
			# "event_date",
			# "location",
			# "month",
			# "taxonomy",
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

	taxonomy = BaseTaxonomicLevelSerializer()
	sources = OriginIdSerializer(many=True)

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
			"month",
			"taxonomy",
			"voucher",
			"year",
			"sources",
		)

	# def get_location(self, obj):
	# 	return GeographicLevelSerializer(GeographicLevel.objects.filter(area__intersects=obj.location).order_by("-rank").first()).data

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


class DownloadOccurrenceSerializer(OccurrenceSerializer):
	taxonomy = serializers.PrimaryKeyRelatedField(read_only=True)


class OccurrenceCountByDateSerializer(serializers.Serializer):
	count = serializers.IntegerField()
	date_field = serializers.SerializerMethodField()

	def __init__(self, *args, view_class, **kwargs):
		self.view_class = view_class
		super().__init__(*args, **kwargs)

	def get_date_field_name(self):
		"""
		Returns the appropriate date field name based on the view class.
		"""
		if self.view_class.__name__ == "OccurrenceCountByTaxonMonthView":
			return "collection_date_month"
		elif self.view_class.__name__ == "OccurrenceCountByTaxonYearView":
			return "collection_date_year"
		else:
			return "sources"

	def get_date_field(self, obj):
		return obj[self.get_date_field_name()]

	def to_representation(self, instance):
		data = super().to_representation(instance)
		if self.view_class.__name__ == "OccurrenceCountByTaxonMonthView":
			data["month"] = data.pop("date_field")
		elif self.view_class.__name__ == "OccurrenceCountByTaxonYearView":
			data["year"] = data.pop("date_field")
		else:
			data["source"] = data.pop("date_field")

		return data


class DynamicSourceSerializer(serializers.Serializer):
	count = serializers.IntegerField()
	source = serializers.CharField()  # Renamed for clarity

	def to_representation(self, instance):
		return {"source": instance["sources__source__basis__name"], "count": instance["count"]}
