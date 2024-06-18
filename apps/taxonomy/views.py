from apps.taxonomy.models import TaxonomicLevel, Authorship
from apps.taxonomy.serializers import BaseTaxonomicLevelSerializer, AuthorshipSerializer
from apps.API.exceptions import CBBAPIException
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .forms import TaxonomicLevelForm, AuthorshipForm
from .serializers import TaxonomicSourcesSerializer


class TaxonSearchView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Search for a taxon by name.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the taxon to search for.",
				type=openapi.TYPE_STRING,
				required=True,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(data=self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		filters = {}
		query = taxon_form.cleaned_data.get("name", None)
		exact = taxon_form.cleaned_data.get("exact", False)

		if not query:
			return Response(BaseTaxonomicLevelSerializer(TaxonomicLevel.objects.none(), many=True).data)

		filters["name__iexact" if exact else "name__icontains"] = query

		queryset = TaxonomicLevel.objects.filter(**filters)[:10]

		return Response(BaseTaxonomicLevelSerializer(queryset, many=True).data)


class TaxonListView(ListAPIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of taxa, with optional filtering.",
		manual_parameters=[
			openapi.Parameter("name", openapi.IN_QUERY, description="Name of the taxon to search for.", type=openapi.TYPE_STRING),
			openapi.Parameter(
				"taxonRank",
				openapi.IN_QUERY,
				description="Rank id of the taxon to search for.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"scientificNameAuthorship",
				openapi.IN_QUERY,
				description="Authorship id of the taxon to search for.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"parent",
				openapi.IN_QUERY,
				description="Parent id of the taxon to search for.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(data=request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		exact = taxon_form.cleaned_data.get("exact", False)
		synonym = taxon_form.cleaned_data.get("synonym", False)
		str_fields = ["name"]
		num_fields = ["parent", "authorship", "rank"]

		filters = {}

		for param in taxon_form.cleaned_data:
			if param != "exact":
				if param in str_fields:
					value = taxon_form.cleaned_data.get(param)

					if value:
						param = f"{param}__iexact" if exact else f"{param}__icontains"
						filters[param] = value

				else:
					value = taxon_form.cleaned_data.get(param)

					if value or isinstance(value, int):
						filters[param] = value

		if synonym:
			filters["accepted"] = False

		queryset = TaxonomicLevel.objects.filter(**filters)

		return Response(BaseTaxonomicLevelSerializer(queryset, many=True).data)


class TaxonCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Retrieve a specific TaxonomicLevel instance by its id",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		return Response(BaseTaxonomicLevelSerializer(taxon).data)


class TaxonParentView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the parents of the taxon given its ID",
		manual_parameters=[
			openapi.Parameter(name="id", in_=openapi.IN_QUERY, description="ID of the taxon", type=openapi.TYPE_INTEGER, required=True),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, 400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		ancestors = taxon.get_ancestors()

		return Response(BaseTaxonomicLevelSerializer(ancestors, many=True).data)


class TaxonChildrenView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the direct children of the taxon given its ID",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the taxonomic level",
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		return Response(BaseTaxonomicLevelSerializer(taxon.get_children(), many=True).data)


class TaxonSynonymView(ListAPIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of taxa, with optional filtering.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve its synonym",
				type=openapi.TYPE_STRING,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		return Response(BaseTaxonomicLevelSerializer(taxon.synonyms, many=True).data)


class TaxonSourceView(ListAPIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of sources, with optional filtering.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve its sources",
				type=openapi.TYPE_STRING,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = self.request.GET

		taxon_id = taxon_form.get("id")

		if not taxon_id:
			raise CBBAPIException(taxon_form.errors, code=400)

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)
		print(taxon)
		return Response(TaxonomicSourcesSerializer(taxon).data)


class AuthorshipCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Authorship"],
		operation_description="Get authorship info by ID",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the authorship",
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		authorship_form = AuthorshipForm(self.request.GET)

		if not authorship_form.is_valid():
			raise CBBAPIException(authorship_form.errors, code=400)

		authorship_id = authorship_form.cleaned_data.get("id")

		if not authorship_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			authorship = Authorship.objects.get(id=authorship_id)
		except Authorship.DoesNotExist:
			raise CBBAPIException("Authorship does not exist.", code=404)

		return Response(AuthorshipSerializer(authorship).data)
