from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import GeographicLevel
from .serializers import GeographicLevelSerializer
from .forms import GeographicLevelForm
from apps.API.exceptions import CBBAPIException


class GeographicLevelDetailView(APIView):
	@swagger_auto_schema(
		operation_description="Retrieve a geographic level by rank and name",
		manual_parameters=[
			openapi.Parameter(
				name="name",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_STRING,
				description="Name of the geographic level",
				required=False,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		geographic_form = GeographicLevelForm(data=self.request.GET)

		filters = {}

		if not geographic_form.is_valid():
			raise CBBAPIException(geographic_form.errors, code=400)

		query = geographic_form.cleaned_data.get("name", None)
		exact = geographic_form.cleaned_data.get("exact", False)

		if not query:
			raise CBBAPIException("Missing name parameter.", code=400)

		filters["name__iexact" if exact else "name__icontains"] = query

		return Response(GeographicLevelSerializer(GeographicLevel.objects.filter(**filters)[:10], many=True).data)


class GeographicLevelIdView(APIView):
	@swagger_auto_schema(
		operation_description="Retrieve a specific geographic level instance by its id",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the geographic level to retrieve",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		geographic_form = GeographicLevelForm(self.request.GET)

		if not geographic_form.is_valid():
			raise CBBAPIException(geographic_form.errors, code=400)

		level_id = geographic_form.cleaned_data.get("id", None)
		if not level_id:
			raise CBBAPIException("Missing id parameter.", code=400)

		try:
			level = GeographicLevel.objects.get(id=level_id)
		except GeographicLevel.DoesNotExist:
			raise CBBAPIException("Geographic level does not exist.", code=404)

		return Response(GeographicLevelSerializer(level).data)


class GeographicLevelListView(APIView):
	@swagger_auto_schema(
		operation_description="List geographic levels with optional filters",
		manual_parameters=[
			openapi.Parameter(
				name="rank", in_=openapi.IN_QUERY, description="Rank of the geographic level", type=openapi.TYPE_STRING, required=False
			),
			openapi.Parameter(
				name="parent",
				in_=openapi.IN_QUERY,
				description="Parent ID of the geographic level",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				name="decimalLatitude",
				in_=openapi.IN_QUERY,
				description="Decimal latitude of the geographic level",
				type=openapi.TYPE_NUMBER,
				required=False,
			),
			openapi.Parameter(
				name="decimalLongitude",
				in_=openapi.IN_QUERY,
				description="Decimal longitude of the geographic level",
				type=openapi.TYPE_NUMBER,
				required=False,
			),
			openapi.Parameter(
				name="coordinateUncertaintyInMeters",
				in_=openapi.IN_QUERY,
				description="Coordinate uncertainty in meters of the geographic level",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		geographic_form = GeographicLevelForm(data=request.GET)

		if not geographic_form.is_valid():
			raise CBBAPIException(geographic_form.errors, code=400)

		str_fields = ["name"]
		num_fields = ["parent", "rank", "decimal_latitude", "decimal_longitude", "coordinate_uncertainty_in_meters"]

		filters = {}

		for param in str_fields:
			value = geographic_form.cleaned_data.get(param)

			if value:
				exact = geographic_form.cleaned_data.get("exact", False)
				param = f"{param}__iexact" if exact else f"{param}__icontains"
				filters[param] = value

		for param in num_fields:
			value = geographic_form.cleaned_data.get(param)

			if value:
				filters[param] = value

		return Response(GeographicLevelSerializer(GeographicLevel.objects.filter(**filters), many=True).data)


class GeographicLevelParent(APIView):
	@swagger_auto_schema(
		operation_description="Get the parents of the geographic level given its ID",
		manual_parameters=[
			openapi.Parameter(
				name="id", in_=openapi.IN_QUERY, description="ID of the geographic level", type=openapi.TYPE_INTEGER, required=True
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		geographic_form = GeographicLevelForm(self.request.GET)

		if not geographic_form.is_valid():
			raise CBBAPIException(geographic_form.errors, code=400)

		level_id = geographic_form.cleaned_data.get("id", None)
		if not level_id:
			raise CBBAPIException("Missing id parameter.", code=400)

		try:
			level = GeographicLevel.objects.get(id=level_id)
		except GeographicLevel.DoesNotExist:
			raise CBBAPIException("Geographic level does not exist.", code=404)

		return Response(GeographicLevelSerializer(level.get_ancestors(), many=True).data)


class GeographicLevelChildren(APIView):
	@swagger_auto_schema(
		operation_description="Get the direct children of the geographic level given its ID",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the geographic level",
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		geographic_form = GeographicLevelForm(self.request.GET)

		if not geographic_form.is_valid():
			raise CBBAPIException(geographic_form.errors, code=400)

		try:
			level_id = geographic_form.cleaned_data.get("id")
		except ValueError:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			level = GeographicLevel.objects.get(id=level_id)
		except GeographicLevel.DoesNotExist:
			raise CBBAPIException("Geographic level does not exist.", code=404)

		return Response(GeographicLevelSerializer(level.get_children(), many=True).data)
