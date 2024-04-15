from rest_framework.response import Response
from rest_framework.views import APIView

from apps.taxonomy.models import TaxonomicLevel
from apps.taxonomy.serializers import TaxonomicLevelSerializer


class SearchTaxonByName(APIView):
	def get(self, request):
		query = request.GET.get('taxon')
		exact = request.GET.get('exact', False)

		if not query:
			return Response(status=400)

		if exact:
			results = TaxonomicLevel.objects.find(query)
		else:
			results = TaxonomicLevel.objects.contains(query)

		return Response(
			TaxonomicLevelSerializer(
				results,
				many=True
			).data
		)


class TaxonCRUD(APIView):
	def get(self, request, id):
		taxon = TaxonomicLevelSerializer(
			TaxonomicLevel.objects.filter(id=id).first()
		)

		return Response(taxon.data)


class TaxonParent(APIView):
	def get(self, request, id):
		taxon = TaxonomicLevelSerializer(
			TaxonomicLevel.objects.filter(id=id).first().parent
		)

		return Response(taxon.data)


class TaxonChildren(APIView):
	def get(self, request, id):
		taxon = TaxonomicLevelSerializer(
			TaxonomicLevel.objects.filter(id=id).first().children,
			many=True
		)

		return Response(taxon.data)
