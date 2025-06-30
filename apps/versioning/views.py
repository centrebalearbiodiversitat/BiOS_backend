from django.db.models import OuterRef, Subquery, Count, IntegerField
from django.db.models.functions import Coalesce
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..API.exceptions import CBBAPIException
from .forms import BasisForm, OriginIdForm, SourceForm
from .models import Basis, OriginId, Source
from .serializers import BasisSerializer, OriginIdSerializer, SourceSerializer, SourceCountSerializer


class BasisSearchView(APIView):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="Retrieve a Basis by name",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the basis to search for.",
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
		basis_form = BasisForm(self.request.GET)

		if not basis_form.is_valid():
			raise CBBAPIException(basis_form.errors, code=400)

		query = basis_form.cleaned_data.get("name")
		exact = basis_form.cleaned_data.get("exact", False)

		if not query:
			raise CBBAPIException("Missing name parameter", code=400)

		filters = {}
		filters["internal_name__iexact" if exact else "internal_name__icontains"] = query

		if filters:
			queryset = Basis.objects.filter(**filters)
		else:
			queryset = Basis.objects.none()

		return Response(BasisSerializer(queryset, many=True).data)


class BasisCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="Get details of a specific basis.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Unique identifier of the basis to retrieve.",
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
		basis_form = BasisForm(data=self.request.GET)

		if not basis_form.is_valid():
			raise CBBAPIException(basis_form.errors, 400)

		basis_id = basis_form.cleaned_data.get("id")

		if not basis_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			occurrence = Basis.objects.get(id=basis_id)
		except Basis.DoesNotExist:
			raise CBBAPIException("Basis does not exist", 404)

		return Response(BasisSerializer(occurrence).data)


class BasisFilter(APIView):
	def get(self, request):
		basis_form = BasisForm(data=self.request.GET)

		if not basis_form.is_valid():
			raise CBBAPIException(basis_form.errors, code=400)

		filters = {}
		for param in basis_form.cleaned_data:
			value = basis_form.cleaned_data.get(param)
			if value or isinstance(value, int):
				filters[param] = value

		q = Basis.objects.filter(**filters)

		if "type" in filters and filters["type"]:
			origin_ids = OriginId.objects.filter(source__basis=OuterRef("id")).values("source__basis_id").annotate(c=Count("id")).values("c")

			q = Basis.objects.filter(**filters).annotate(originid_count=Subquery(origin_ids, output_field=IntegerField())).order_by("-originid_count")

		return q


class BasisListView(BasisFilter):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="List Basiss with optional filters",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the basis to search for.",
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
				description="Origin of the basis to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(BasisSerializer(super().get(request), many=True).data)


class BasisCountView(BasisFilter):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="List Basiss with optional filters",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the basis to search for.",
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
				description="Origin of the basis to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(super().get(request).count())


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


class SourceFilter(APIView):
	def get(self, request):
		return Source.objects.all().select_related("basis")


class SourceListView(SourceFilter):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="List all the Sources",
		manual_parameters=[],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(SourceSerializer(super().get(request), many=True).data)


class SourceListCountView(SourceFilter):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="List all the Sources",
		manual_parameters=[],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(super().get(request).count())


class SourceStatisticsFilter(APIView):
	def get(self, request):
		basis_form = BasisForm(data=self.request.GET)

		if not basis_form.is_valid():
			raise CBBAPIException(basis_form.errors, code=400)

		basis_id = basis_form.cleaned_data.get("id")
		if not basis_id:
			raise CBBAPIException("Missing id parameter", 400)

		oq = (
			OriginId.objects.filter(source=OuterRef("id"))
			.exclude(source__data_type=Source.OCCURRENCE, occurrence__in_geography_scope=False)
			.values("source")
			.annotate(ent_count=Count("id"))
			.values("ent_count")
		)

		sources = Source.objects.filter(basis_id=basis_id).annotate(count=Coalesce(Subquery(oq[:1]), 0))

		return sources


class SourceStatisticsView(SourceStatisticsFilter):
	@swagger_auto_schema(
		tags=["Versioning"],
		operation_description="List Sources with optional filters",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Id of the basis to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(SourceCountSerializer(super().get(request).order_by("-count"), many=True).data)


class OriginIdCRUDView(APIView):
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
		os_form = OriginIdForm(data=self.request.GET)

		if not os_form.is_valid():
			raise CBBAPIException(os_form.errors, 400)

		os_id = os_form.cleaned_data.get("id")
		if not os_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			os = OriginId.objects.get(id=os_id)
		except OriginId.DoesNotExist:
			raise CBBAPIException("Source does not exist", 404)

		return Response(OriginIdSerializer(os).data)
