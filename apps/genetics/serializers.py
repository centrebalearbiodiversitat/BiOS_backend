from rest_framework import serializers

from common.utils.serializers import CaseModelSerializer
from .models import Marker, Sequence


class SuperMarkerSerializer(CaseModelSerializer):
	total = serializers.IntegerField()

	class Meta:
		model = Marker
		fields = ["id", "name", "product", "total"]


class MarkerSerializer(CaseModelSerializer):
	class Meta:
		model = Marker
		fields = "__all__"


class SequenceSerializer(CaseModelSerializer):
	class Meta:
		model = Sequence
		fields = "__all__"
