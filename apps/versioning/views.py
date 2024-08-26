from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..API.exceptions import CBBAPIException
from .forms import OriginSourceForm, SourceForm
from .models import OriginSource, Source
from .serializers import OriginSourceSerializer, SourceSerializer


class SourceSearchView(APIView):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="Retrieve a Source by name",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the source to search for.",
				type=openapi.TYPE_STRING,
				required=True,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Whether to search for an exact match or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		source_form = SourceForm(self.request.GET)

		if not source_form.is_valid():
			raise CBBAPIException(source_form.errors, code=400)

		query = source_form.cleaned_data.get("name")
		exact = source_form.cleaned_data.get("exact", False)

		if not query:
			raise CBBAPIException("Missing name parameter", code=400)

		filters = {}
		filters["name__iexact" if exact else "name__icontains"] = query

		if filters:
			queryset = Source.objects.filter(**filters)
		else:
			queryset = Source.objects.none()

		return Response(SourceSerializer(queryset, many=True).data)


class SourceCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="Get details of a specific source.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the source to retrieve.",
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
		source_form = SourceForm(data=self.request.GET)

		if not source_form.is_valid():
			raise CBBAPIException(source_form.errors, 400)

		source_id = source_form.cleaned_data.get("id")
		if not source_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			occurrence = Source.objects.get(id=source_id)
		except Source.DoesNotExist:
			raise CBBAPIException("Source does not exist", 404)

		return Response(SourceSerializer(occurrence).data)


class SourceListView(APIView):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="List Sources with optional filters",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the source to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"accepted",
				openapi.IN_QUERY,
				description="Whether to search for accepted or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
				default=False,
			),
			openapi.Parameter(
				"origin",
				openapi.IN_QUERY,
				description="Origin of the source to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		source_form = SourceForm(data=self.request.GET)

		if not source_form.is_valid():
			raise CBBAPIException(source_form.errors, code=400)

		filters = {}
		for param in source_form.cleaned_data:
			value = source_form.cleaned_data.get(param)
			if value or isinstance(value, int):
				filters[param] = value
		if filters:
			queryset = Source.objects.filter(**filters)
		else:
			queryset = Source.objects.none()

		if not queryset.exists():
			raise CBBAPIException("No taxonomic levels found for the given filters.", 404)

		return Response(SourceSerializer(queryset, many=True).data)


class OriginSourceCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="Get details of a specific source.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the source to retrieve.",
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
		os_form = OriginSourceForm(data=self.request.GET)

		if not os_form.is_valid():
			raise CBBAPIException(os_form.errors, 400)

		os_id = os_form.cleaned_data.get("id")
		if not os_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			os = OriginSource.objects.get(id=os_id)
		except OriginSource.DoesNotExist:
			raise CBBAPIException("Source does not exist", 404)

		return Response(OriginSourceSerializer(os).data)
