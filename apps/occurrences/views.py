from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Occurrence
from .serializers import OccurrenceSerializer
from .forms import OccurrenceForm

TRANSFORM_PARAM = {
	"basisOfRecord": "basis_of_record",
	"basisOfRecordDisplay": "basis_of_record_display",
	"year": "collection_date_year",
	"month": "collection_date_month",
	"day": "collection_date_day",
	"coordinateUncertaintyInMeters": "coordinatesUncertaintyMeters",
	"decimalLatitude": "latitude",
	"decimalLongitude": "longitude",
	"elevation": "elevationMeters",
	"depth": "depthMeters"
}

class OccurrenceDetail(APIView):
	@swagger_auto_schema(
        operation_description="Get details of a specific occurrence.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_QUERY,
                description="Unique identifier of the occurrence to retrieve.",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: "Success",
			204: "No Content",
            400: "Bad Request - Invalid query parameters",
			404: "Not Found",
        }
    )
	def get(self, request):
		occurr_form = OccurrenceForm(self.request.GET)

		if not occurr_form.is_valid():
			raise ValidationError(occurr_form.errors)

		occur_id = request.query_params.get("id")
		occurrence = Occurrence.objects.get(id=occur_id)

		serializer = OccurrenceSerializer(occurrence)
		return Response(serializer.data)



class OccurrenceFilter(APIView):
	def get(self, request):
		form = request.GET
		occu_form = {}

		for param in form:
			if param in TRANSFORM_PARAM:
				occu_form[TRANSFORM_PARAM[param]] = form.get(param)
			else:
				occu_form[param] = form.get(param)

		occurr_form = OccurrenceForm(occu_form)

		if not occurr_form.is_valid():
			return Response(occurr_form.errors, status=400)

		filters = {}
		for param in occurr_form.cleaned_data:
			value = occurr_form.cleaned_data.get(param)
			if value:
				filters[param] = value

		return self.filter_queryset(filters)

	def filter_queryset(self, filters):
		queryset = Occurrence.objects.filter(**filters)
		return queryset


class OccurrenceList(OccurrenceFilter):
	@swagger_auto_schema(
        operation_description="Filter occurrences based on query parameters.",
        manual_parameters=[
            openapi.Parameter(
                name=field,
                in_=openapi.IN_QUERY,
                description=f"Filter occurrences by {field} field.",
                type=openapi.TYPE_STRING,  # Adjust data type based on model field
            )
            for field in ["taxonomy", "voucher", "geographicalLocation", "year",
                         "month", "day", "basisOfRecord"]
        ],
        responses={
            200: "Success",
			204: "No Content",
            400: "Bad Request - Invalid query parameters",
			404: "Not Found"
        }
    )
	def filter_queryset(self, filters):
		queryset = super().filter_queryset(filters)
		return queryset

	def get(self, request):
		queryset = super().get(request)
		serializer = OccurrenceSerializer(queryset, many=True)
		return Response(serializer.data)


class OccurrenceCount(OccurrenceFilter):
	@swagger_auto_schema(
        operation_description="Filter occurrences based on query parameters.",
		request_body=OccurrenceSerializer,
        responses={
            200: "Success",
			204: "No Content",
            400: "Bad Request - Invalid query parameters",
			404: "Not Found"
        }
    )
	def filter_queryset(self, filters):
		queryset = super().filter_queryset(filters)
		return queryset.count()

	def get(self, request):
		queryset = super().get(request)
		return Response({'count': queryset})
