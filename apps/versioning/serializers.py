from apps.versioning.models import Source, Batch, OriginSource
from common.utils.serializers import CaseModelSerializer


class SourceSerializer(CaseModelSerializer):
	class Meta:
		model = Source
		fields = "__all__"


class OriginSourceSerializer(CaseModelSerializer):
	source = SourceSerializer(read_only=True)

	class Meta:
		model = OriginSource
		fields = "__all__"
