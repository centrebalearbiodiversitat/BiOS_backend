from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from .forms import GeneForm, ProductForm, ProducesForm, SequenceForm
from apps.occurrences.forms import OccurrenceForm
from apps.taxonomy.models import TaxonomicLevel
from apps.geography.models import GeographicLevel
from .serializers import GeneSerializer, ProductSerializer, ProducesSerializer, SequenceSerializer
from ..API.exceptions import CBBAPIException
from .models import Gene, Product, Produces, Sequence, Occurrence


class GeneCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Get details of a specific gene.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the gene to retrieve.",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		],
		responses={
			200: "Success",
			400: "Bad Request",
			404: "Not Found",
		},
	)
	def get(self, request):
		gene_form = GeneForm(data=self.request.GET)

		if not gene_form.is_valid():
			raise CBBAPIException(gene_form.errors, 400)

		gene_id = gene_form.cleaned_data.get("id")
		if not gene_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			gene = Gene.objects.get(id=gene_id)
		except Gene.DoesNotExist:
			raise CBBAPIException("Gene does not exist", 404)

		return Response(GeneSerializer(gene).data)


class GeneDetailView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Search for a gene by name.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the gene to search for.",
				type=openapi.TYPE_STRING,
				required=True,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
				default=False,
			),
		],
		responses={
			200: "Success",
			400: "Bad Request",
			404: "Not Found",
		},
	)
	def get(self, request):
		gene_form = GeneForm(data=self.request.GET)

		if not gene_form.is_valid():
			raise CBBAPIException(gene_form.errors, 400)

		filters = {}
		query = gene_form.cleaned_data.get("name", None)
		exact = gene_form.cleaned_data.get("exact", False)

		if not query:
			raise CBBAPIException("You must specify a name", 400)

		filters["name__iexact" if exact else "name__icontains"] = query

		return Response(GeneSerializer(Gene.objects.filter(**filters)[:10], many=True).data)


class GeneListView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="List genes with optional filters",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Name of the gene to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		gene_form = GeneForm(data=self.request.GET)

		if not gene_form.is_valid():
			raise CBBAPIException(gene_form.errors, 400)

		taxon = gene_form.cleaned_data.get("taxonomy")
		if not taxon:
			raise CBBAPIException("Missing taxon id parameter", 400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		queryset = Gene.objects.filter(
			Q(produces__sequence__occurrence__taxonomy=taxon) |
			Q(produces__sequence__occurrence__taxonomy__lft__gte=taxon.lft) |
			Q(produces__sequence__occurrence__taxonomy__rght__lte=taxon.rght),
		).distinct()

		return Response(GeneSerializer(queryset, many=True).data)


class ProductCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Get details of a specific product.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the product to retrieve.",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		],
		responses={
			200: "Success",
			400: "Bad Request",
			404: "Not Found",
		},
	)
	def get(self, request):
		product_form = ProductForm(data=self.request.GET)

		if not product_form.is_valid():
			raise CBBAPIException(product_form.errors, 400)

		product_id = product_form.cleaned_data.get("id")
		if not product_id:
			raise CBBAPIException("Missing product id parameter", 400)

		try:
			product = Product.objects.get(id=product_id)
		except Product.DoesNotExist:
			raise CBBAPIException("Product does not exist", 404)

		return Response(ProductSerializer(product).data)


class ProductDetailView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Search for a product by name.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the product to search for.",
				type=openapi.TYPE_STRING,
				required=True,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
				default=False,
			),
		],
		responses={
			200: "Success",
			400: "Bad Request",
			404: "Not Found",
		},
	)
	def get(self, request):
		product_form = ProductForm(data=self.request.GET)

		if not product_form.is_valid():
			raise CBBAPIException(product_form.errors, code=400)

		filters = {}
		query = product_form.cleaned_data.get("name", None)
		exact = product_form.cleaned_data.get("exact", False)

		if not query:
			return Response(ProductSerializer(Product.objects.none(), many=True).data)

		filters["name__iexact" if exact else "name__icontains"] = query

		return Response(ProductSerializer(Product.objects.filter(**filters)[:10], many=True).data)


class ProductListView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="List products with optional filters",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the product to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
				default=False,
			),
			openapi.Parameter(
				"batch",
				openapi.IN_QUERY,
				description="Batch to search for.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"sources",
				openapi.IN_QUERY,
				description="Source ID to search for.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"accepted",
				openapi.IN_QUERY,
				description="Whether to search for accepted or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
				default=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		product_form = ProductForm(data=self.request.GET)

		if not product_form.is_valid():
			return Response(product_form.errors, status=400)

		str_fields = ["name", "unidecode_name"]
		exact = product_form.cleaned_data.get("exact", False)

		filters = {}
		for param in product_form.cleaned_data:
			if param != "exact":
				if param in str_fields:
					value = product_form.cleaned_data.get(param)

					if value:
						param = f"{param}__iexact" if exact else f"{param}__icontains"
						filters[param] = value
				else:
					value = product_form.cleaned_data.get(param)
					if value or isinstance(value, int):
						filters[param] = value

		if filters:
			queryset = Product.objects.filter(**filters)
		else:
			queryset = Product.objects.none()

		return Response(ProductSerializer(queryset, many=True).data)


class ProducesCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Get details of a specific produce.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the produce to retrieve.",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		],
		responses={
			200: "Success",
			400: "Bad Request",
			404: "Not Found",
		},
	)
	def get(self, request):
		produce_form = ProducesForm(data=self.request.GET)

		if not produce_form.is_valid():
			raise CBBAPIException(produce_form.errors, 400)

		produce_id = produce_form.cleaned_data.get("id")
		if not produce_id:
			raise CBBAPIException("Missing produces relation id parameter", 400)

		try:
			produce = Produces.objects.get(id=produce_id)
		except Produces.DoesNotExist:
			raise CBBAPIException("Produces relation does not exist", 404)

		return Response(ProducesSerializer(produce).data)


class ProducesListView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="List products with optional filters",
		manual_parameters=[
			openapi.Parameter(
				"batch",
				openapi.IN_QUERY,
				description="Batch to search for.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"sources",
				openapi.IN_QUERY,
				description="Source ID to search for.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"accepted",
				openapi.IN_QUERY,
				description="Whether to search for accepted or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
				default=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		product_form = ProducesForm(data=self.request.GET)

		if not product_form.is_valid():
			return Response(product_form.errors, status=400)

		str_fields = ["name", "unidecode_name"]
		exact = product_form.cleaned_data.get("exact", False)

		filters = {}
		for param in product_form.cleaned_data:
			if param != "exact":
				if param in str_fields:
					value = product_form.cleaned_data.get(param)

					if value:
						param = f"{param}__iexact" if exact else f"{param}__icontains"
						filters[param] = value
				else:
					value = product_form.cleaned_data.get(param)
					if value or isinstance(value, int):
						filters[param] = value

		if filters:
			queryset = Produces.objects.filter(**filters)
		else:
			queryset = Produces.objects.none()

		return Response((ProducesSerializer(queryset, many=True)).data)


class SequenceCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Get details of a specific genetic feature.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the genetic feature to retrieve.",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		],
		responses={
			200: "Success",
			400: "Bad Request",
			404: "Not Found",
		},
	)
	def get(self, request):
		seq_form = SequenceForm(data=self.request.GET)

		if not seq_form.is_valid():
			raise CBBAPIException(seq_form.errors, 400)

		seq_id = seq_form.cleaned_data.get("id")
		if not seq_id:
			raise CBBAPIException("Missing sequence id", 400)

		try:
			gfs = Sequence.objects.get(id=seq_id)
		except Sequence.DoesNotExist:
			raise CBBAPIException("Sequence does not exist", 404)

		return Response(SequenceSerializer(gfs).data)


class SequenceSearchView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Search for a genetic feature by definition.",
		manual_parameters=[
			openapi.Parameter(
				"definition",
				openapi.IN_QUERY,
				description="Definition of the genetic feature to search for.",
				type=openapi.TYPE_STRING,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request"},
	)
	def get(self, request):
		seq_form = SequenceForm(data=self.request.GET)
		if not seq_form.is_valid():
			raise CBBAPIException(seq_form.errors, code=400)

		definition = seq_form.cleaned_data.get("definition", None)

		return Response(SequenceSerializer(Sequence.objects.filter(definition__icontains=definition), many=True).data)


class SequenceFilter(APIView):
	def get(self, request):
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		filters = {}
		taxon_ids = set()
		value = occur_form.cleaned_data.get("taxonomy")

		if not value:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			obj = TaxonomicLevel.objects.get(id=value.id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		filters["taxonomy__lft__gte"] = obj.lft
		filters["taxonomy__rght__lte"] = obj.rght
		taxon_ids.add(obj.id)
		synonyms = obj.synonyms.filter(accepted=False)

		for synonym in synonyms:
			taxon_ids.add(synonym.id)

		if not filters:
			return Sequence.objects.none()

		try:
			genetic_features = Sequence.objects.filter(occurrence__taxonomy__in=taxon_ids)

			return genetic_features
		except Sequence.DoesNotExist:
			raise CBBAPIException("Sequence do not exist.", code=404)


class SequenceListView(SequenceFilter):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Retrieve the sequences of a taxonomic level by its id",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="ID of the taxon from which all its sequences will be retrieved",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(SequenceSerializer(super().get(request), many=True).data)


class SequenceListCountView(SequenceFilter):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Retrieve the sequences count of a taxonomic level by its id.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon from which all its sequences will be retrieved",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(super().get(request).count())
