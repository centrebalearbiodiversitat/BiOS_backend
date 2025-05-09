from django.db.models import Count, Q, OuterRef, Subquery, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.taxonomy.models import TaxonomicLevel
from apps.API.exceptions import CBBAPIException
from apps.versioning.models import Basis

from .forms import MarkerForm, SequenceForm, SequenceListForm
from .models import Marker, Sequence
from .serializers import (
	MarkerCountSerializer,
	MarkerSerializer,
	SequenceSerializer,
	SequenceAggregationSerializer,
	SequenceCSVSerializer
)
from common.utils.views import CSVDownloadMixin
from common.utils.serializers import get_paginated_response


def genetic_schema(tags: str = "Genetic", operation_id: str = None, operation_description: str = None, manual_parameters: list = None):
	return swagger_auto_schema(
		tags=[tags],
		operation_id=operation_id,
		operation_description=operation_description,
		manual_parameters=manual_parameters or [
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Marker ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
],
		responses={
			200: "Success",
			400: "Bad Request",
			404: "Not Found"
		}
	)


class MarkerCRUDView(APIView):
	@genetic_schema(
		operation_id="Search marker by ID",
		operation_description="Get details of a specific marker by its ID.",
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
	@genetic_schema(
		operation_id="Search marker by name",
		operation_description="Search for a marker by name.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Marker name",
				type=openapi.TYPE_STRING,
				required=True,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
				default=False,
			),
		]
	)
	def get(self, request):
		marker_form = MarkerForm(data=self.request.GET)

		if not marker_form.is_valid():
			raise CBBAPIException(marker_form.errors, 400)

		filters = {}
		query = marker_form.cleaned_data.get("name", None)
		exact = marker_form.cleaned_data.get("exact", False)

		if not query:
			raise CBBAPIException("You must specify a marker name", 400)

		filters["name__iexact" if exact else "name__icontains"] = query

		return Response(MarkerSerializer(Marker.objects.filter(**filters)[:10], many=True).data)


# class MarkerOccurFilter(APIView):
# 	def get(self, request, in_geography_scope=False):
# 		seq_form = SequenceForm(data=self.request.GET)

# 		if not seq_form.is_valid():
# 			raise CBBAPIException(seq_form.errors, 400)

# 		taxon_id = seq_form.cleaned_data.get("taxonomy")
# 		if not taxon_id:
# 			raise CBBAPIException("Missing taxon id parameter", 400)

# 		all_markers = Marker.objects.all()

# 		marker_id = seq_form.cleaned_data.get("marker")
# 		if not marker_id:
# 			raise CBBAPIException("Missing marker id parameter", 400)

# 		try:
# 			taxon = TaxonomicLevel.objects.get(id=taxon_id)
# 		except TaxonomicLevel.DoesNotExist:
# 			raise CBBAPIException("Taxonomic level does not exist", 404)

# 		sequence_count = (
# 			Sequence.objects.filter(occurrence__taxonomy__in=taxon.get_descendants(include_self=True), markers=OuterRef("pk"))
# 			.values("markers")
# 			.distinct()
# 			.annotate(count=Case(When(markers__pk=marker_id, then=Count("pk")), default=0, output_field=IntegerField()))
# 			.values("count")
# 		)

# 		queryset = all_markers.annotate(count=Subquery(sequence_count))

# 		return queryset


# class MarkerOccurListView(MarkerOccurFilter):
# 	def get(self, request):
# 		return Response(SequenceSerializer(super().get(request), many=True).data)


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

		# queryset = Marker.objects.filter(sequence__in=seq_queryset)
		# queryset = queryset.annotate(total=Count("id")).order_by("-total")

		accepted_marker = Marker.objects.filter(Q(accepted=True, id=OuterRef("id")) | Q(synonyms=OuterRef("id"), accepted=True))

		queryset = Marker.objects.filter(sequence__in=seq_queryset)
		queryset = queryset.annotate(accepted_id=accepted_marker.values("id")[:1]).annotate(total=Count("id"))

		acc_count = {}
		for marker in queryset:
			if marker.accepted_id not in acc_count:
				acc_count[marker.accepted_id] = 0
			acc_count[marker.accepted_id] += marker.total

		total_case = Case(
			*[When(id=key, then=Value(value)) for key, value in acc_count.items()],
			default=Value(0),  # Default value if not in the map
			output_field=IntegerField(),
		)
		queryset = Marker.objects.filter(id__in=acc_count.keys()).annotate(total=total_case)

		return queryset.order_by("-total")


class MarkerListView(MarkerFilter):
	@genetic_schema(
		operation_id="List markers by taxon ID",
		operation_description="Retrieve the markers of a taxon by its ID.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		]
	)
	def get(self, request):
		return Response(MarkerCountSerializer(super().get(request), many=True).data)


class MarkerCountView(MarkerFilter):
	@genetic_schema(
		operation_id="Count markers by taxon ID",
		operation_description="Retrieve the markers count of a taxon by its ID.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		]
	)
	def get(self, request):
		return Response(super().get(request).count())


# class MarkerTaxonCountListView(APIView):
# 	@swagger_auto_schema(
# 		tags=["Genetic"],
# 		operation_id="Count markers by taxonomy",
# 		operation_description="Retrieve the markers count of a taxonomic level by its id.",
# 		manual_parameters=[
# 			openapi.Parameter(
# 				"taxonomy",
# 				openapi.IN_QUERY,
# 				description="ID of the taxon from which all its markers will be retrieved",
# 				type=openapi.TYPE_INTEGER,
# 				required=True,
# 			)
# 		],
# 		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
# 	)
# 	def get(self, request):
# 		taxon_id = request.GET.get("taxonomy")
# 		if not taxon_id:
# 			raise CBBAPIException("Missing taxon id parameter", 400)

# 		try:
# 			taxon = TaxonomicLevel.objects.get(id=taxon_id)
# 		except TaxonomicLevel.DoesNotExist:
# 			raise CBBAPIException("Taxonomic level does not exist", 404)

# 		all_markers = Marker.objects.all()

# 		# sequence_count = (
# 		# 	Sequence.objects.filter(occurrence__taxonomy__in=taxon.get_descendants(include_self=True), markers=OuterRef("pk"))
# 		# 	.values("markers")
# 		# 	.distinct()
# 		# 	.annotate(count=Count("pk"))
# 		# 	.values("count")
# 		# )


# 		# --- Subconsulta Refinada ---
# 		sequence_subquery = (
# 			Sequence.objects.filter(
# 				occurrence__taxonomy__in=taxon.get_descendants(include_self=True),
# 				markers=OuterRef("pk") # 1. Filtra por el Marker relevante
# 			)
# 			.order_by() # 2. Limpia cualquier ordenación por defecto (importante para consistencia de agregación)
# 			.values("markers") # 3. Especifica el campo de agrupación (el ID del marker)
# 			.annotate(c=Count("pk")) # 4. Realiza la agregación (conteo) por grupo
# 			.values("c") # 5. Selecciona *únicamente* el valor agregado ('c')
# 		)
# 		# Nota: No usamos .[:1] aquí. Dejamos que Subquery maneje la expectativa de valor único.

# 		queryset = all_markers.annotate(
# 			# Asegúrate de especificar output_field para la Subquery
# 			count=Coalesce(Subquery(sequence_subquery, output_field=IntegerField()), 0)
# 		)

# 		# --- Depuración (Opcional pero útil) ---
# 		# Antes de ejecutar/serializar, puedes ver el SQL generado:
# 		# try:
# 		#     print(str(queryset.query))
# 		# except Exception as e:
# 		#     print(f"Error generating query SQL: {e}")
# 		# --------------------------------------

# 		# Intenta ejecutar la consulta aquí para aislar el error si persiste
# 		# try:
# 		#     list(queryset) # Fuerza la ejecución de la consulta
# 		# except Exception as e:
# 		#      print(f"Error executing queryset: {e}")
# 		#      # Aquí podrías lanzar una excepción o manejar el error
# 		#      raise e # Vuelve a lanzar el error para ver el traceback completo

# 		serializer = MarkerSerializer(queryset, many=True)
# 		return Response(serializer.data)


class SequenceCRUDView(APIView):
	@genetic_schema(
		operation_id="Search genetic occurrence by ID",
		operation_description="Get details of a specific genetic occurrence.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Genetic occurrence ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		]
	)
	def get(self, request):
		seq_form = SequenceForm(data=self.request.GET)

		if not seq_form.is_valid():
			raise CBBAPIException(seq_form.errors, 400)

		seq_id = seq_form.cleaned_data.get("id")
		if not seq_id:
			raise CBBAPIException("Missing sequence ID", 400)

		try:
			gfs = Sequence.objects.get(id=seq_id)
		except Sequence.DoesNotExist:
			raise CBBAPIException("Sequence does not exist", 404)

		return Response(SequenceSerializer(gfs).data)


# class SequenceSearchView(APIView):
# 	@genetic_schema(
# 		operation_id="Search genetic occurrence by definition",
# 		operation_description="Search for a genetic occurrence by NCBI definition.",
# 		manual_parameters=[
# 			openapi.Parameter(
# 				"definition",
# 				openapi.IN_QUERY,
# 				description="NCBI definition",
# 				type=openapi.TYPE_STRING,
# 				required=True,
# 			)
# 		]
# 	)
# 	def get(self, request):
# 		seq_form = SequenceForm(data=self.request.GET)
# 		if not seq_form.is_valid():
# 			raise CBBAPIException(seq_form.errors, code=400)
#
# 		definition = seq_form.cleaned_data.get("definition", None)
# 		if not definition:
# 			raise CBBAPIException("Missing definition parameter", code=400)
#
# 		return Response(SequenceSerializer(Sequence.objects.filter(definition__icontains=definition), many=True).data)


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
			filters &= Q(markers=marker) | Q(markers__synonyms=marker)

		in_geography_scope = seq_form.cleaned_data.get("in_geography_scope", None)
		if in_geography_scope is not None:
			filters &= Q(occurrence__in_geography_scope=in_geography_scope)

		return Sequence.objects.filter(filters).order_by("id").distinct("id") if filters else Sequence.objects.none()


class SequenceListView(SequenceFilter):
	@genetic_schema(
		operation_id="List genetic occurrences by taxon ID",
		operation_description="Retrieve the genetic occurrences of a taxon by its ID.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		]
	)
	def get(self, request):
		query = super().get(request).prefetch_related("sources", "markers").select_related("occurrence", "occurrence__taxonomy")

		return Response(get_paginated_response(request, query, SequenceSerializer))


class SequenceCountView(SequenceFilter):
	@genetic_schema(
		operation_id="Count genetic occurrences by taxon ID",
		operation_description="Retrieve the genetic occurrence count of a taxon by its ID.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		]
	)
	def get(self, request):
		return Response(super().get(request).count())


class SequenceListCSVView(SequenceFilter):
	@genetic_schema(
		operation_id="List genetic occurrences by taxon ID (CSV)",
		operation_description="Retrieve a CSV with the genetic occurrences of a taxon by its ID.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		]
	)
	def get(self, request):
		query = super().get(request).prefetch_related("sources", "markers").select_related("occurrence", "occurrence__taxonomy")

		return CSVDownloadMixin.generate_csv(SequenceCSVSerializer(query, many=True).data, filename="genetic_occurrences.csv")


class SequenceSourceCountView(APIView):
	@genetic_schema(
		operation_id="Count genetic occurrences of a taxon per source",
		operation_description="Retrieve the genetic occurrence count of a taxon per source.",
		manual_parameters=[
			openapi.Parameter(
				"marker",
				openapi.IN_QUERY,
				description="Marker ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		]
	)
	def get(self, request):
		seq_form = SequenceForm(data=self.request.GET)

		if not seq_form.is_valid():
			raise CBBAPIException(seq_form.errors, 400)

		taxon_id = seq_form.cleaned_data.get("taxonomy")
		if not taxon_id:
			raise CBBAPIException("Missing taxon id parameter", 400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		marker_id = seq_form.cleaned_data.get("marker")
		if not marker_id:
			raise CBBAPIException("Missing marker id parameter", 400)
		try:
			marker = Marker.objects.get(id=marker_id)
		except Marker.DoesNotExist:
			raise CBBAPIException("Marker does not exist", 404)

		queryset = Sequence.objects.filter(Q(occurrence__taxonomy=taxon) & Q(markers=marker)).values("sources__source__basis__internal_name").annotate(count=Count("id")).order_by("-count")
		return Response(SequenceAggregationSerializer(queryset, many=True).data)


class SequenceSourceDownload(APIView):

	def get(self, request):
		seq_form = SequenceForm(data=self.request.GET)
		if not seq_form.is_valid():
			raise CBBAPIException(seq_form.errors, 400)

		taxon_id = seq_form.cleaned_data.get("taxonomy")
		if not taxon_id:
			raise CBBAPIException("Missing taxon id parameter", 400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		marker_id = seq_form.cleaned_data.get("marker")
		if not marker_id:
			raise CBBAPIException("Missing taxon id parameter", 400)
		try:
			marker = Marker.objects.get(id=marker_id)
		except Marker.DoesNotExist:
			raise CBBAPIException("Marker does not exist", 404)

		source = seq_form.cleaned_data.get("source")
		if not source:
			raise CBBAPIException("Missing source name parameter", 400)

		try:
			src = Basis.objects.get(internal_name__icontains=source)
		except Marker.DoesNotExist:
			raise CBBAPIException("Source level does not exist", 404)

		queryset = Sequence.objects.filter(Q(occurrence__taxonomy=taxon) & Q(markers=marker) & Q(sources__source__basis=src))

		return Response(SequenceSerializer(queryset, many=True).data)


class SequenceSourceCSVDownloadView(SequenceSourceDownload):
	@genetic_schema(
		operation_id="Download genetic occurrences by taxon and source (CSV)",
		operation_description="Retrieve a CSV with the genetic occurrences of a taxon by its ID and source.",
		manual_parameters=[
			openapi.Parameter(
				"marker",
				openapi.IN_QUERY,
				description="Marker ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
			openapi.Parameter(
				"source",
				openapi.IN_QUERY,
				description="Source name (e.g., ncbi)",
				type=openapi.TYPE_STRING,
				required=True,
			),
		]
	)
	def get(self, request):
		response = super().get(request)
		flattened_data = CSVDownloadMixin.flatten_json(response.data, ["sources", "markers"])

		return CSVDownloadMixin.generate_csv(flattened_data, filename="sequences.csv")
