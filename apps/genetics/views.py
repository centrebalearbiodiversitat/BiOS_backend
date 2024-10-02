from django.db.models import Count, Q, OuterRef
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.taxonomy.models import TaxonomicLevel

from ..API.exceptions import CBBAPIException
from .forms import MarkerForm, SequenceForm, SequenceListForm
from .models import Marker, Sequence
from .serializers import SuperMarkerSerializer, MarkerSerializer, SequenceSerializer


class MarkerCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Get details of a specific marker.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the marker to retrieve.",
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
		marker_form = MarkerForm(data=self.request.GET)

		if not marker_form.is_valid():
			raise CBBAPIException(marker_form.errors, 400)

		marker_id = marker_form.cleaned_data.get("id")
		if not marker_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			marker = Marker.objects.get(id=marker_id)
		except Marker.DoesNotExist:
			raise CBBAPIException("Marker does not exist", 404)

		return Response(MarkerSerializer(marker).data)


class MarkerSearchView(APIView):
	@swagger_auto_schema(
		tags=["Genetic"],
		operation_description="Search for a marker by name.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the marker to search for.",
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
		marker_form = MarkerForm(data=self.request.GET)

		if not marker_form.is_valid():
			raise CBBAPIException(marker_form.errors, 400)

		filters = {}
		query = marker_form.cleaned_data.get("name", None)
		exact = marker_form.cleaned_data.get("exact", False)

		if not query:
			raise CBBAPIException("You must specify a name", 400)

		filters["name__iexact" if exact else "name__icontains"] = query

		return Response(MarkerSerializer(Marker.objects.filter(**filters)[:10], many=True).data)


class MarkerFilter(APIView):
	def get(self, request):
		marker_form = MarkerForm(data=self.request.GET)

		if not marker_form.is_valid():
			raise CBBAPIException(marker_form.errors, 400)

		taxon_id = marker_form.cleaned_data.get("taxonomy")
		if not taxon_id:
			raise CBBAPIException("Missing taxon id parameter", 400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		# Filter all markers by taxon
		queryset = Marker.objects.filter(
			Q(sequence__occurrence__taxonomy=taxon)
			| Q(sequence__occurrence__taxonomy__lft__gte=taxon.lft, sequence__occurrence__taxonomy__rght__lte=taxon.rght),
		)

		# Annotate with the accepted id
		accepted_marker = Marker.objects.filter(Q(accepted=True, id=OuterRef("id")) | Q(synonyms=OuterRef("id"), accepted=True))

		queryset = queryset.annotate(accepted_marker=accepted_marker.values("id")[:1])

		queryset = Marker.objects.filter(id__in=queryset.values("accepted_marker")).annotate(
			total=queryset.filter(accepted_marker=OuterRef("id"))
			.values("accepted_marker")
			.annotate(total=Count("accepted_marker"))
			.values("total")[:1]
		)

		queryset = queryset.filter(total__gte=1).order_by("-total")

		return queryset


class MarkerListView(MarkerFilter):
	def get(self, request):
		return Response(SuperMarkerSerializer(super().get(request), many=True).data)


class MarkerCountView(MarkerFilter):
	def get(self, request):
		return Response(super().get(request).count())


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
		if not definition:
			raise CBBAPIException("Missing definition parameter", code=400)

		return Response(SequenceSerializer(Sequence.objects.filter(definition__icontains=definition), many=True).data)


class SequenceFilter(APIView):
	def get(self, request):
		seq_form = SequenceListForm(data=request.GET)

		if not seq_form.is_valid():
			raise CBBAPIException(seq_form.errors, 400)

		taxon = seq_form.cleaned_data.get("taxonomy")

		if not taxon:
			raise CBBAPIException("Missing taxonomy parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		return Sequence.objects.filter(
			Q(occurrence__taxonomy=taxon) | Q(occurrence__taxonomy__lft__gte=taxon.lft, occurrence__taxonomy__rght__lte=taxon.rght)
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


class SequenceCountView(SequenceFilter):
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
