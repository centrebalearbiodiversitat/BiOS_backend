from django.db.models import Q, Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from .forms import GeneForm, SequenceForm, SequenceListForm
from apps.occurrences.forms import OccurrenceForm
from apps.taxonomy.models import TaxonomicLevel
from .serializers import GeneSerializer, SequenceSerializer, MarkerSerializer
from ..API.exceptions import CBBAPIException
from .models import Gene, Sequence


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
			Q(produces__sequence__occurrence__taxonomy=taxon)
			| Q(produces__sequence__occurrence__taxonomy__lft__gte=taxon.lft)
			| Q(produces__sequence__occurrence__taxonomy__rght__lte=taxon.rght),
		).distinct()

		return Response(GeneSerializer(queryset, many=True).data)


class MarkersListView(APIView):
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
			Q(sequence__occurrence__taxonomy=taxon)
			| Q(sequence__occurrence__taxonomy__lft__gte=taxon.lft,
				sequence__occurrence__taxonomy__rght__lte=taxon.rght),
		).annotate(total=Count('id')).filter(total__gte=10).order_by("-total")

		return Response(MarkerSerializer(queryset, many=True).data)


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
		seq_form = SequenceListForm(data=request.GET)

		if not seq_form.is_valid():
			raise CBBAPIException(seq_form.errors, 400)

		taxon = seq_form.cleaned_data.get("taxon_id")

		if not taxon:
			raise CBBAPIException("Missing taxonomy parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		return Sequence.objects.filter(
			Q(occurrence__taxonomy=taxon) |
			Q(
				occurrence__taxonomy__lft__gte=taxon.lft,
				occurrence__taxonomy__rght__lte=taxon.rght
			)
		)


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
