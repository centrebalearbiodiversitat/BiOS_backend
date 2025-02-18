from django.db.models import Count, Q, OuterRef
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.taxonomy.models import TaxonomicLevel
from common.utils.serializers import get_paginated_response

from ..API.exceptions import CBBAPIException
from .forms import MarkerForm, SequenceForm, SequenceListForm
from .models import Marker, Sequence
from .serializers import MarkerCountSerializer, MarkerSerializer, SequenceSerializer


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
		seq_queryset = Sequence.objects.filter(occurrence__taxonomy__in=taxon.get_descendants(include_self=True)).distinct()

		in_geography_scope = marker_form.cleaned_data.get("in_geography_scope", None)
		if in_geography_scope is not None:
			seq_queryset = seq_queryset.filter(occurrence__in_geography_scope=in_geography_scope)

		queryset = Marker.objects.filter(sequence__in=seq_queryset)
		queryset = queryset.annotate(total=Count("id")).order_by("-total")

		# Annotate with the accepted id
		# accepted_marker = Marker.objects.filter(Q(accepted=True, id=OuterRef("id")) | Q(synonyms=OuterRef("id"), accepted=True))
		#
		# queryset = queryset.annotate(accepted_marker=accepted_marker.values("id")[:1])
		#
		# queryset = Marker.objects.filter(id__in=queryset.values("accepted_marker")).annotate(
		# 	total=queryset.filter(accepted_marker=OuterRef("id"))
		# 	.values("accepted_marker")
		# 	.annotate(total=Count("accepted_marker"))
		# 	.values("total")[:1]
		# )

		return queryset


class MarkerListView(MarkerFilter):
	def get(self, request):
		return Response(MarkerCountSerializer(super().get(request), many=True).data)


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

		filters = Q()
		taxon = seq_form.cleaned_data.get("taxonomy")
		if taxon:
			try:
				taxon = TaxonomicLevel.objects.get(id=taxon)
				filters |= Q(occurrence__taxonomy=taxon) | Q(occurrence__taxonomy__lft__gte=taxon.lft, occurrence__taxonomy__rght__lte=taxon.rght)
			except TaxonomicLevel.DoesNotExist:
				raise CBBAPIException("Taxonomic level does not exist", 404)

		marker = seq_form.cleaned_data.get("marker")
		if marker:
			filters &= Q(markers=marker)

		in_geography_scope = seq_form.cleaned_data.get("in_geography_scope", None)
		if in_geography_scope is not None:
			filters &= Q(occurrence__in_geography_scope=in_geography_scope)

		return Sequence.objects.filter(filters) if filters else Sequence.objects.none()


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
		query = super().get(request).prefetch_related("sources", "markers").select_related("occurrence", "occurrence__taxonomy")

		return Response(get_paginated_response(request, query, SequenceSerializer))


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
		sequences = super().get(request)
		return Response(f"{sequences.filter(occurrence__in_geography_scope=True).count()} / {sequences.count()}")
