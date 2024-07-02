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
	SPECIAL_FILTERS = {"geographical_location": GeographicLevel, "taxonomy": TaxonomicLevel}

	def get(self, request):
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		filters = {}
		for param in occur_form.cleaned_data:
			value = occur_form.cleaned_data.get(param)
			if value:
				klass = OccurrenceFilter.SPECIAL_FILTERS.get(param, None)
				if klass:
					try:
						obj = klass.objects.get(id=value.id)
					except klass.DoesNotExist:
						raise CBBAPIException(f"{param} does not exist", 404)

					filters[f"{param}__lft__gte"] = obj.lft
					filters[f"{param}__rght__lte"] = obj.rght
				else:
					filters[param] = value

		if not filters:
			return Occurrence.objects.none()

		return Occurrence.objects.filter(**filters)


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


class OccurrenceTaxonView(APIView):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_description="Filter occurrences based on query parameters.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by taxon id.",
				type=openapi.TYPE_INTEGER,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		taxonomy = occur_form.cleaned_data.get("taxonomy", None)
		add_synonyms = occur_form.cleaned_data.get("add_synonyms")

		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)

		query = Q(id=taxonomy.id)
		if add_synonyms:
			query |= Q(synonyms=taxonomy, accepted=False)

		taxa = TaxonomicLevel.objects.filter(query).distinct()

		if not taxa:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		filters = None
		for taxon in taxa:
			if filters:
				filters |= Q(taxonomy=taxon) | Q(taxonomy__lft__gte=taxon.lft, taxonomy__rght__lte=taxon.rght)
			else:
				filters = Q(taxonomy=taxon) | Q(taxonomy__lft__gte=taxon.lft, taxonomy__rght__lte=taxon.rght)

		if filters:
			query = Occurrence.objects.filter(filters).distinct()
		else:
			query = Occurrence.objects.none()

		return Response(OccurrenceSerializer(query, many=True).data)
