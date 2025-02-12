from rest_framework import serializers

from apps.versioning.serializers import OriginIdSerializer
from common.utils.serializers import CaseModelSerializer
from .models import Marker, Sequence


class SuperMarkerSerializer(CaseModelSerializer):
	total = serializers.IntegerField()

	class Meta:
		model = Marker
		fields = ["id", "name", "total"]


class MarkerSerializer(CaseModelSerializer):

	class Meta:
		model = Marker
		fields = "__all__"

class MarkerCountSerializer(CaseModelSerializer):
	count = serializers.IntegerField()
	class Meta:
		model = Marker
		fields = "__all__"


class SequenceSerializer(CaseModelSerializer):
    sources = OriginIdSerializer(many=True)
    markers = MarkerSerializer(many=True)

    class Meta:
        model = Sequence
        fields = "__all__"

		
class SequenceAggregationSerializer(CaseModelSerializer):
    source = serializers.CharField(source='sources__source__basis__internal_name')
    count = serializers.IntegerField()   

    class Meta:
        model = Sequence
        fields = ["source", "count"]
		
class DownloadSequenceSourceSerializer(SequenceSerializer):
	taxonomy = serializers.PrimaryKeyRelatedField(read_only=True)