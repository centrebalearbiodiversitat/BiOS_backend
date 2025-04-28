from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.API.exceptions import CBBAPIException

from .forms import GeographicLevelForm
from .models import GeographicLevel
from .serializers import GeographicLevelSerializer


class GeographicLevelDetailView(APIView):
	@swagger_auto_schema(
        tags=["Geography"],
        operation_id="Search geographic level by name",
        operation_description="Retrieve a geographic level by name (supports exact and partial match)",
        manual_parameters=[
            openapi.Parameter(
                name="name",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Name of the geographic level to search for",
                required=True,
            ),
            openapi.Parameter(
                name="exact",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Search for an exact match (case-insensitive)",
                required=False,
            ),
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
			return Response([])

		filters["name__iexact" if exact else "name__icontains"] = query

		return Response(GeographicLevelSerializer(GeographicLevel.objects.filter(**filters)[:10], many=True).data)


class GeographicLevelIdView(APIView):
	@swagger_auto_schema(
		tags=["Geography"],
		operation_id= "Search geographic level by id",
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
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			level = GeographicLevel.objects.get(id=level_id)
		except GeographicLevel.DoesNotExist:
			raise CBBAPIException("Geographic level does not exist.", code=404)

		return Response(GeographicLevelSerializer(level).data)


class GeographicLevelFilter(APIView):
	def get(self, request):
		geographic_form = GeographicLevelForm(data=request.GET)

		if not geographic_form.is_valid():
			raise CBBAPIException(geographic_form.errors, code=400)

		filters = {}

		str_fields = ["name"]
		for param in str_fields:
			value = geographic_form.cleaned_data.get(param)

			if value:
				exact = geographic_form.cleaned_data.get("exact", False)
				param = f"{param}__iexact" if exact else f"{param}__icontains"
				filters[param] = value

		num_fields = ["parent", "rank", "decimal_latitude", "decimal_longitude", "coordinate_uncertainty_in_meters"]
		for param in num_fields:
			value = geographic_form.cleaned_data.get(param)

			if value:
				filters[param] = value

		if filters:
			query = GeographicLevel.objects.filter(**filters)
		else:
			query = GeographicLevel.objects.none()
		return query


class GeographicLevelListView(GeographicLevelFilter):
	@swagger_auto_schema(
        tags=["Geography"],
        operation_id="List geographic levels",
        operation_description="List geographic levels with optional filters",
        manual_parameters=[
            openapi.Parameter(name="name", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by name", required=False),
            openapi.Parameter(name="parent", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by parent ID", required=False),
            openapi.Parameter(name="rank", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by rank", required=False),
            openapi.Parameter(name="decimalLatitude", in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="Filter by decimal latitude", required=False),
            openapi.Parameter(name="decimalLongitude", in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="Filter by decimal longitude", required=False),
            openapi.Parameter(name="coordinateUncertaintyInMeters", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by coordinate uncertainty", required=False),
            openapi.Parameter(name="exact", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description="Use exact match for 'name' parameter (case-insensitive)", required=False),
        ],
        responses={200: "Success", 400: "Bad Request"},
    )
	def get(self, request):
		return Response(GeographicLevelSerializer(super().get(request), many=True).data)


class GeographicLevelCountView(GeographicLevelFilter):
	@swagger_auto_schema(
        tags=["Geography"],
        operation_id="Count geographic levels",
        operation_description="Get the count of geographic levels based on optional filters",
        manual_parameters=[
            openapi.Parameter(name="name", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by name", required=False),
            openapi.Parameter(name="parent", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by parent ID", required=False),
            openapi.Parameter(name="rank", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by rank", required=False),
            openapi.Parameter(name="decimalLatitude", in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="Filter by decimal latitude", required=False),
            openapi.Parameter(name="decimalLongitude", in_=openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="Filter by decimal longitude", required=False),
            openapi.Parameter(name="coordinateUncertaintyInMeters", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by coordinate uncertainty", required=False),
            openapi.Parameter(name="exact", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description="Use exact match for 'name' parameter (case-insensitive)", required=False),
        ],
        responses={200: "Success", 400: "Bad Request"},
    )
	def get(self, request):
		return Response(super().get(request).count())


class GeographicLevelParent(APIView):
	@swagger_auto_schema(
        tags=["Geography"],
        operation_id="Get parents of a geographic level",
        operation_description="Retrieve the ancestors (parents) of a specific geographic level given its ID",
        manual_parameters=[
            openapi.Parameter(name="id", in_=openapi.IN_QUERY, description="ID of the geographic level", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
    )
	def get(self, request):
		geographic_form = GeographicLevelForm(self.request.GET)

		if not geographic_form.is_valid():
			raise CBBAPIException(geographic_form.errors, code=400)

		level_id = geographic_form.cleaned_data.get("id", None)
		if not level_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			level = GeographicLevel.objects.get(id=level_id)
		except GeographicLevel.DoesNotExist:
			raise CBBAPIException("Geographic level does not exist", code=404)

		return Response(GeographicLevelSerializer(level.get_ancestors(), many=True).data)


class GeographicLevelChildren(APIView):
	@swagger_auto_schema(
        tags=["Geography"],
        operation_id="Get children of a geographic level",
        operation_description="Retrieve the direct children of a specific geographic level given its ID",
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
			raise CBBAPIException("Geographic level does not exist", code=404)

		return Response(GeographicLevelSerializer(level.get_children(), many=True).data)
