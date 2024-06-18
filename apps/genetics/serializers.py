from common.utils.serializers import CaseModelSerializer
from .models import Gene, Product, Produces, GeneticFeatures


class GeneSerializer(CaseModelSerializer):
	class Meta:
		model = Gene
		fields = "__all__"


class ProductSerializer(CaseModelSerializer):
	class Meta:
		model = Product
		fields = "__all__"


class ProducesSerializer(CaseModelSerializer):
	class Meta:
		model = Produces
		fields = "__all__"


class GeneticFeaturesSerializer(CaseModelSerializer):
	class Meta:
		model = GeneticFeatures
		fields = "__all__"
