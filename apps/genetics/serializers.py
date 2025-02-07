from rest_framework import serializers

from common.utils.serializers import CaseModelSerializer
from .models import Marker, Sequence, Product
from apps.versioning.serializers import OriginIdSerializer
from apps.occurrences.serializers import BaseOccurrenceSerializer


class MarkerCountSerializer(CaseModelSerializer):
	total = serializers.IntegerField()

	class Meta:
		model = Marker
		fields = ["id", "name", "total"]


class ProductSerializer(CaseModelSerializer):
	class Meta:
		model = Product
		fields = "__all__"


class BaseMarkerSerializer(CaseModelSerializer):
	class Meta:
		model = Marker
		fields = ("id", "name", "accepted")


class MarkerSerializer(BaseMarkerSerializer):
	synonyms = BaseMarkerSerializer(many=True)
	products = ProductSerializer(many=True)

	class Meta(BaseMarkerSerializer.Meta):
		# fields = ("id", "name", "accepted")
		fields = "__all__"


class SequenceSerializer(CaseModelSerializer):
	sources = OriginIdSerializer(many=True)
	markers = BaseMarkerSerializer(many=True)
	occurrence = BaseOccurrenceSerializer()

	class Meta:
		model = Sequence
		exclude = ("batch", )
