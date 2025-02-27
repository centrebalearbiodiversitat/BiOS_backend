from rest_framework import serializers

from common.utils.serializers import CaseModelSerializer
from .models import Marker, Sequence
from apps.versioning.serializers import OriginIdSerializer
from apps.occurrences.serializers import OccurrenceSerializer


class MarkerCountSerializer(CaseModelSerializer):
	total = serializers.IntegerField()

	class Meta:
		model = Marker
		fields = ["id", "name", "total"]


class BaseMarkerSerializer(CaseModelSerializer):
	class Meta:
		model = Marker
		fields = ("id", "name", "accepted")


class MarkerSerializer(BaseMarkerSerializer):
	synonyms = BaseMarkerSerializer(many=True)

	class Meta(BaseMarkerSerializer.Meta):
		fields = BaseMarkerSerializer.Meta.fields + (
			"product",
			"synonyms",
		)


class SequenceSerializer(CaseModelSerializer):
	sources = OriginIdSerializer(many=True)
	markers = BaseMarkerSerializer(many=True)
	occurrence = OccurrenceSerializer()

	class Meta:
		model = Sequence
		exclude = ("batch",)


class SequenceCSVSerializer(CaseModelSerializer):
	taxonomy = serializers.SerializerMethodField()
	source = serializers.SerializerMethodField()
	external_id = serializers.SerializerMethodField()
	markers = serializers.SerializerMethodField()

	def get_taxonomy(self, obj):
		return str(obj.occurrence.taxonomy)

	def get_source(self, obj):
		return obj.sources.all()[0].source.basis.get_name()

	def get_external_id(self, obj):
		return obj.sources.all()[0].external_id

	def get_markers(self, obj):
		return list(obj.markers.values_list("name", flat=True))

	class Meta:
		model = Sequence
		exclude = ("batch", "occurrence", "sources", "isolate")


class SequenceAggregationSerializer(CaseModelSerializer):
	source = serializers.CharField(source="sources__source__basis__internal_name")
	count = serializers.IntegerField()

	class Meta:
		model = Sequence
		fields = ["source", "count"]


class DownloadSequenceSourceSerializer(SequenceSerializer):
	taxonomy = serializers.PrimaryKeyRelatedField(read_only=True)
