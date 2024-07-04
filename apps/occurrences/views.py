from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Occurrence
from .serializers import OccurrenceSerializer
from .forms import OccurrenceForm
from ..API.exceptions import CBBAPIException
from ..geography.models import GeographicLevel
from ..taxonomy.models import TaxonomicLevel


class OccurrenceCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_description="Get details of a specific occurrence.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the occurrence to retrieve.",
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
		occur_form = OccurrenceForm(data=self.request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		occur_id = occur_form.cleaned_data.get("id")
		if not occur_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			occurrence = Occurrence.objects.get(id=occur_id)
		except Occurrence.DoesNotExist:
			raise CBBAPIException("Occurrence does not exist", 404)

		return Response(OccurrenceSerializer(occurrence).data)


class OccurrenceFilter(APIView):
	def get(self, request):
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		# Filter taxon and synonyms
		taxonomy = occur_form.cleaned_data.get("taxonomy", None)
		add_synonyms = occur_form.cleaned_data.get("add_synonyms")

		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)

		taxon_query = Q(id=taxonomy.id)
		if add_synonyms:
			taxon_query |= Q(synonyms=taxonomy, accepted=False)

		taxa = TaxonomicLevel.objects.filter(taxon_query).distinct()

		if not taxa:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		# Filter occurrences based on filtered taxa
		occus_filters = Q()
		gl = occur_form.cleaned_data.get("geographical_location", None)
		if gl:
			occus_filters = Q(geographical_location__id=gl.id) | Q(geographical_location__lft__gte= gl.lft, geographical_location__rght__lte= gl.rght)

		filters = Q()
		for taxon in taxa:
			filters |= Q(taxonomy__id=taxon.id) & occus_filters | Q(taxonomy__lft__gte=taxon.lft, taxonomy__rght__lte=taxon.rght) & occus_filters

		if filters:
			query = Occurrence.objects.filter(filters).distinct()
		else:
			query = Occurrence.objects.none()

		return query


class OccurrenceListView(OccurrenceFilter):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_description="Filter occurrences based on query parameters.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by taxon id.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"voucher",
				openapi.IN_QUERY,
				description="Filter occurrences by voucher field.",
				type=openapi.TYPE_STRING,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"geographicalLocation",
				openapi.IN_QUERY,
				description="Filter occurrences by geographical location id.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"year",
				openapi.IN_QUERY,
				description="Filter occurrences by year field.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"month",
				openapi.IN_QUERY,
				description="Filter occurrences by month field.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"day",
				openapi.IN_QUERY,
				description="Filter occurrences by day field.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"basisOfRecord",
				openapi.IN_QUERY,
				description="Filter occurrences by basis of record field.",
				type=openapi.TYPE_STRING,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"coordinateUncertaintyInMeters",
				openapi.IN_QUERY,
				description="Filter occurrences by the coordinate uncertainty in meters.",
				type=openapi.TYPE_STRING,  # Ajusta el tipo de dato según el campo del modelo
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(OccurrenceSerializer(super().get(request), many=True).data)


class OccurrenceCountView(OccurrenceFilter):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_description="Counts the filtered occurrences based on the query parameters.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by taxon id.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"voucher",
				openapi.IN_QUERY,
				description="Filter occurrences by voucher field.",
				type=openapi.TYPE_STRING,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"geographicalLocation",
				openapi.IN_QUERY,
				description="Filter occurrences by geographical location id.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"year",
				openapi.IN_QUERY,
				description="Filter occurrences by year field.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"month",
				openapi.IN_QUERY,
				description="Filter occurrences by month field.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"day",
				openapi.IN_QUERY,
				description="Filter occurrences by day field.",
				type=openapi.TYPE_INTEGER,  # Ajusta el tipo de dato según el campo del modelo
			),
			openapi.Parameter(
				"basisOfRecord",
				openapi.IN_QUERY,
				description="Filter occurrences by basis of record field.",
				type=openapi.TYPE_STRING,  # Ajusta el tipo de dato según el campo del modelo
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(super().get(request).count())
