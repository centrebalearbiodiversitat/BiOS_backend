from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.taxonomy.models import TaxonomicLevel

from ..API.exceptions import CBBAPIException
from .forms import OccurrenceForm
from .models import Occurrence
from .serializers import OccurrenceSerializer, BaseOccurrenceSerializer


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
	def filter_by_range(self, filters, field_name, min_value, max_value):
		if min_value:
			filters &= Q(**{f"{field_name}__gte": min_value})
		if max_value:
			filters &= Q(**{f"{field_name}__lte": max_value})
		return filters

	def get(self, request):
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		# Filter taxon and synonyms
		taxonomy = occur_form.cleaned_data.get("taxonomy", None)
		add_synonyms = occur_form.cleaned_data.get("add_synonyms")

		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)

		taxon_query = Q(id=taxonomy)
		if add_synonyms:
			taxon_query |= Q(synonyms=taxonomy, accepted=False)

		taxa = TaxonomicLevel.objects.filter(taxon_query).distinct()

		if not taxa:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		filters = Q()
		for taxon in taxa:
			filters |= Q(taxonomy__id=taxon.id) | Q(taxonomy__lft__gte=taxon.lft, taxonomy__rght__lte=taxon.rght)

		gl = occur_form.cleaned_data.get("geographical_location", None)
		if gl:
			filters &= Q(geographical_location__id=gl.id) | Q(
				geographical_location__lft__gte=gl.lft, geographical_location__rght__lte=gl.rght
			)

		voucher = occur_form.cleaned_data.get("voucher", None)
		if voucher:
			filters &= Q(voucher__icontains=voucher)

		range_parameters = ["decimal_latitude", "decimal_longitude", "coordinate_uncertainty_in_meters", "elevation", "depth"]

		for param in range_parameters:
			filters = self.filter_by_range(
				filters,
				param,
				occur_form.cleaned_data.get(f"{param}_min"),
				occur_form.cleaned_data.get(f"{param}_max"),
			)

		query = Occurrence.objects.filter(filters).distinct()

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
				"decimal_latitude_min",
				openapi.IN_QUERY,
				description="Minimum latitude",
				type=openapi.TYPE_NUMBER,
				format=openapi.FORMAT_DECIMAL,
			),
			openapi.Parameter(
				"decimal_latitude_max",
				openapi.IN_QUERY,
				description="Maximum latitude",
				type=openapi.TYPE_NUMBER,
				format=openapi.FORMAT_DECIMAL,
			),
			openapi.Parameter(
				"decimal_longitude_min",
				openapi.IN_QUERY,
				description="Minimum longitude",
				type=openapi.TYPE_NUMBER,
				format=openapi.FORMAT_DECIMAL,
			),
			openapi.Parameter(
				"decimal_longitude_max",
				openapi.IN_QUERY,
				description="Maximum longitude",
				type=openapi.TYPE_NUMBER,
				format=openapi.FORMAT_DECIMAL,
			),
			openapi.Parameter(
				"coordinate_uncertainty_in_meters_min",
				openapi.IN_QUERY,
				description="Minimum coordinate uncertainty in meters",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"coordinate_uncertainty_in_meters_max",
				openapi.IN_QUERY,
				description="Maximum coordinate uncertainty in meters",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter("elevation_min", openapi.IN_QUERY, description="Minimum elevation", type=openapi.TYPE_INTEGER),
			openapi.Parameter("elevation_max", openapi.IN_QUERY, description="Maximum elevation", type=openapi.TYPE_INTEGER),
			openapi.Parameter("depth_min", openapi.IN_QUERY, description="Minimum depth", type=openapi.TYPE_INTEGER),
			openapi.Parameter("depth_max", openapi.IN_QUERY, description="Maximum depth", type=openapi.TYPE_INTEGER),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(BaseOccurrenceSerializer(super().get(request), many=True).data)


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
