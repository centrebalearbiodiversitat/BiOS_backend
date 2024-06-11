from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .forms import GeneForm, ProductForm, ProducesForm, GeneticFeaturesForm
from .serializers import GeneSerializer, ProductSerializer, ProducesSerializer, GeneticFeaturesSerializer
from ..API.exceptions import CBBAPIException
from .models import Gene, Product, Produces, GeneticFeatures


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
			raise CBBAPIException("Missing gene ID", 400)

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

		queryset = Gene.objects.filter(**filters)[:10]

		return Response(GeneSerializer(queryset, many=True).data)


class GeneListView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="List genes with optional filters",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the gene to search for.",
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
		gene_form = GeneForm(data=self.request.GET)

		if not gene_form.is_valid():
			raise CBBAPIException(gene_form.errors, 400)

		str_fields = ["name", "unidecode_name"]
		exact = gene_form.cleaned_data.get("exact", False)

		filters = {}

		for param in gene_form.cleaned_data:
			if param != "exact":
				if param in str_fields:
					value = gene_form.cleaned_data.get(param)

					if value:
						param = f"{param}__iexact" if exact else f"{param}__icontains"
						filters[param] = value
				else:
					value = gene_form.cleaned_data.get(param)
					if value or isinstance(value, int):
						filters[param] = value

		if filters:
			queryset = Gene.objects.filter(**filters)

		else:
			raise CBBAPIException("You must specify a field to filter by", 400)

		return Response((GeneSerializer(queryset, many=True)).data)


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
			raise CBBAPIException("Missing product ID", 400)

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
			raise CBBAPIException("You must specify a name", 400)

		filters["name__iexact" if exact else "name__icontains"] = query

		queryset = Product.objects.filter(**filters)[:10]

		return Response(ProductSerializer(queryset, many=True).data)


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
			raise CBBAPIException("You must specify a field to filter by", 400)

		return Response((ProductSerializer(queryset, many=True)).data)


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
			raise CBBAPIException("Missing produce ID", 400)

		try:
			produce = Produces.objects.get(id=produce_id)
		except Produces.DoesNotExist:
			raise CBBAPIException("Produce does not exist", 404)

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
			raise CBBAPIException("You must specify a field to filter by", 400)

		return Response((ProducesSerializer(queryset, many=True)).data)


class GeneticFeaturesCRUDView(APIView):
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
		gfs_form = GeneticFeaturesForm(data=self.request.GET)

		if not gfs_form.is_valid():
			raise CBBAPIException(gfs_form.errors, 400)

		gfs_id = gfs_form.cleaned_data.get("id")
		if not gfs_id:
			raise CBBAPIException("Missing genetic feature ID", 400)

		try:
			gfs = GeneticFeatures.objects.get(id=gfs_id)
		except GeneticFeatures.DoesNotExist:
			raise CBBAPIException("Genetic feature does not exist", 404)

		return Response(GeneticFeaturesSerializer(gfs).data)


class GeneticFeaturesDetailView(APIView):
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
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
			),
		],
		responses={200: "Success", 400: "Bad Request"},
	)
	def get(self, request):
		gfs_form = GeneticFeaturesForm(data=self.request.GET)
		if not gfs_form.is_valid():
			raise CBBAPIException(gfs_form.errors, code=400)

		filters = {}
		query = gfs_form.cleaned_data.get("definition", None)
		exact = gfs_form.cleaned_data.get("exact", False)

		if not query:
			raise CBBAPIException("You must specify a definition", 400)

		filters["definition__iexact" if exact else "definition__icontains"] = query

		queryset = GeneticFeatures.objects.filter(**filters)[:10]

		return Response(GeneticFeaturesSerializer(queryset, many=True).data)


class GeneticFeaturesListView(APIView):
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
				"isolate",
				openapi.IN_QUERY,
				description="ID of the isolate to filter for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"bp",
				openapi.IN_QUERY,
				description="Number of bp to filter for",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"definition",
				openapi.IN_QUERY,
				description="Definition of the genetic feature to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"dataFileDivision",
				openapi.IN_QUERY,
				description="Whether to search for accepted or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"publishedDate",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"collectionDateYear",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"collectionDateMonth",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"collectionDateDay",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"moleculeType",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"sequenceVersion",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"products",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		gfs_form = GeneticFeaturesForm(data=self.request.GET)

		if not gfs_form.is_valid():
			return Response(gfs_form.errors, status=400)

		str_fields = ["definition"]
		exact = gfs_form.cleaned_data.get("exact", False)

		filters = {}

		for param in gfs_form.cleaned_data:
			if param != "exact":
				if param in str_fields:
					value = gfs_form.cleaned_data.get(param)

					if value:
						param = f"{param}__iexact" if exact else f"{param}__icontains"
						filters[param] = value
				else:
					value = gfs_form.cleaned_data.get(param)
					if value or isinstance(value, int):
						filters[param] = value

		if filters:
			queryset = GeneticFeatures.objects.filter(**filters)

		else:
			raise CBBAPIException("You must specify a field to filter by", 400)

		return Response((GeneticFeaturesSerializer(queryset, many=True)).data)
