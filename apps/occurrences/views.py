from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Occurrence
from .serializers import OccurrenceSerializer
from .forms import OccurrenceForm
from ..geography.models import GeographicLevel
from ..taxonomy.models import TaxonomicLevel


class OccurrenceDetail(APIView):
	@swagger_auto_schema(
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
			204: "No Content",
			400: "Bad Request",
			404: "Not Found",
		},
	)
	def get(self, request):
		occurr_form = OccurrenceForm(data=self.request.GET)

		if not occurr_form.is_valid():
			raise ValidationError(occurr_form.errors)

		occur_id = request.query_params.get("id")
		try:
			occurrence = Occurrence.objects.get(id=occur_id)
		except Occurrence.DoesNotExist:
			raise Http404

		return Response(OccurrenceSerializer(occurrence).data)


class OccurrenceFilter(APIView):
	SPECIAL_FILTERS = {
		'geographical_location': GeographicLevel,
		'taxonomy': TaxonomicLevel
	}

	def get(self, request):
		occu_form = OccurrenceForm(data=request.GET)
		if not occu_form.is_valid():
			return Response(occu_form.errors, status=400)

		filters = {}
		for param in occu_form.cleaned_data:
			value = occu_form.cleaned_data.get(param)
			if value:
				klass = OccurrenceFilter.SPECIAL_FILTERS.get(param, None)
				if klass:
					try:
						obj = klass.objects.get(id=value.id)
					except klass.DoesNotExist:
						raise Http404(f"{param} does not exist")

					filters[f"{param}__lft__gte"] = obj.lft
					filters[f"{param}__rght__lte"] = obj.rght
				else:
					filters[param] = value

		if not filters:
			return Occurrence.objects.none()

		return Occurrence.objects.filter(**filters)


class OccurrenceList(OccurrenceFilter):
	@swagger_auto_schema(
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
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(OccurrenceSerializer(super().get(request), many=True).data)


class OccurrenceCount(OccurrenceFilter):
	@swagger_auto_schema(
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
