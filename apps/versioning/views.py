from django.db.models import OuterRef, Subquery, Count, IntegerField, Q, ManyToManyField, Sum
from django.db.models.functions import Coalesce
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.views import APIView

from django.apps import apps
from apps.API.exceptions import CBBAPIException
from apps.versioning.forms import BasisForm, OriginIdForm, SourceForm
from apps.versioning.models import Basis, OriginId, Source
from apps.versioning.serializers import BasisSerializer, OriginIdSerializer, SourceSerializer, SourceCountSerializer

from common.utils.custom_swag_schema import custom_swag_schema


MANUAL_PARAMETERS = [
	openapi.Parameter(
		"id",
		openapi.IN_QUERY,
		description="Unique identifier of the source to retrieve.",
		type=openapi.TYPE_INTEGER,
		required=True,
	)
]


class BasisSearchView(APIView):
	@custom_swag_schema(
		tags="Versioning",
		operation_id="Get basis by name",
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
	@custom_swag_schema(
		tags="Versioning",
		operation_id="Get basis details",
		operation_description="Get details of a specific basis.",
		manual_parameters=MANUAL_PARAMETERS,
	)
	def get(self, request):
		basis_form = BasisForm(data=self.request.GET)

		if not basis_form.is_valid():
			raise CBBAPIException(basis_form.errors, 400)

		basis_id = basis_form.cleaned_data.get("id")

		if not basis_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			basis = Basis.objects.get(id=basis_id)
		except Basis.DoesNotExist:
			raise CBBAPIException("Basis does not exist", 404)

		return Response(BasisSerializer(basis).data)


class BasisFilter(APIView):
	def get(self, request):
		basis_form = BasisForm(data=self.request.GET)

		if not basis_form.is_valid():
			raise CBBAPIException(basis_form.errors, code=400)

		exact = basis_form.cleaned_data.get("exact", False)
		basis_form.cleaned_data.pop("exact", None)

		filters = {}
		for param in basis_form.cleaned_data:
			value = basis_form.cleaned_data.get(param)

			if param == "name":
				if value:
					filters["internal_name__iexact" if exact else "internal_name__icontains"] = value
					continue

			if value or isinstance(value, int):
				filters[param] = value

		q = Basis.objects.filter(**filters)

		return q


class BasisListView(BasisFilter):
	@custom_swag_schema(
		tags="Versioning",
		operation_id="List basis",
		operation_description="List of basis.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the basis to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Whether to search for an exact match or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"type",
				openapi.IN_QUERY,
				description="Type of the basis to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
	)
	def get(self, request):
		return Response(BasisSerializer(super().get(request), many=True).data)


class BasisCountView(BasisFilter):
	@custom_swag_schema(
		tags="Versioning",
		operation_id="Count basis",
		operation_description="Return the total number of the basis.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the basis to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Whether to search for an exact match or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			),
			openapi.Parameter(
				"type",
				openapi.IN_QUERY,
				description="Type of the basis to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
	)
	def get(self, request):
		return Response(super().get(request).count())


# class SourceSearchView(APIView):
# 	@swagger_auto_schema(
#         tags=["Versioning"],
#         operation_id="Get a source by its name",
#         operation_description="Retrieve a source by its name.",
#         manual_parameters=[
#             openapi.Parameter(
#                 "name",
#                 openapi.IN_QUERY,
#                 description="Source name",
#                 type=openapi.TYPE_STRING,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 "exact",
#                 openapi.IN_QUERY,
#                 description="Whether to search for an exact match or not",
#                 type=openapi.TYPE_BOOLEAN,
#                 required=False,
#             ),
#         ],
#         responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
#     )
# 	def get(self, request):
# 		source_form = SourceForm(self.request.GET)
#
# 		if not source_form.is_valid():
# 			raise CBBAPIException(source_form.errors, code=400)
#
# 		query = source_form.cleaned_data.get("name")
# 		exact = source_form.cleaned_data.get("exact", False)
#
# 		if not query:
# 			raise CBBAPIException("Missing name parameter", code=400)
#
# 		filters = {}
# 		filters["basis__name__iexact" if exact else "basis__name__icontains"] = query
#
# 		if filters:
# 			queryset = Source.objects.filter(**filters)
# 		else:
# 			queryset = Source.objects.none()
#
# 		return Response(SourceSerializer(queryset, many=True).data)


class SourceCRUDView(APIView):
	@custom_swag_schema(
		tags="Versioning",
		operation_id="Get source details",
		operation_description="Get details of a specific source.",
		manual_parameters=MANUAL_PARAMETERS,
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
		basis_name = self.request.GET.get("basis", None)

		sources = Source.objects.filter()

		if basis_name is not None:
			sources = sources.filter(basis__name__icontains=basis_name)

		return sources.select_related("basis")


class SourceListView(SourceFilter):
	@custom_swag_schema(
		tags="Versioning",
		operation_description="List all the Sources",
		manual_parameters=[
			openapi.Parameter(
				"basis",
				openapi.IN_QUERY,
				description="Basis ID of the source to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(SourceSerializer(super().get(request), many=True).data)


class SourceListCountView(SourceFilter):
	@custom_swag_schema(
		tags="Versioning",
		operation_description="List all the Sources",
		manual_parameters=[
			openapi.Parameter(
				"basis",
				openapi.IN_QUERY,
				description="Basis ID of the source to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
		],
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
		sources = Source.objects.filter(basis_id=basis_id).exclude(data_type=Source.TAXON_DATA).annotate(count=Coalesce(Subquery(oq[:1]), 0))

		oq_taxon_data = (
			OriginId.objects.filter(
				Q(iucndata__sources__source=OuterRef("id")) |
				Q(taxontag__sources__source=OuterRef("id"))
			)
			.values("id")
			.annotate(ent_count=Count("id"))
			.values("ent_count")
		)
		sources = sources.union(
			Source.objects.filter(basis_id=basis_id, data_type=Source.TAXON_DATA)
							.annotate(count=Coalesce(Subquery(oq_taxon_data[:1]), 0)),
			all=True
		)

		return sources.union(sources)


class SourceStatisticsView(SourceStatisticsFilter):
	@custom_swag_schema(
		tags="Versioning",
		operation_description="List Sources with optional filters",
		manual_parameters=MANUAL_PARAMETERS,
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(SourceCountSerializer(super().get(request).order_by("-count"), many=True).data)


class SourceCountView(SourceFilter):
	@custom_swag_schema(
		tags="Versioning", operation_id="Count sources", operation_description="Count the number of sources."
	)
	def get(self, request):
		return Response(super().get(request).count())


class OriginIdCRUDView(APIView):
	@custom_swag_schema(
		tags="Versioning",
		operation_id="Get origin id details",
		operation_description="Get details of a specific source.",
		manual_parameters=MANUAL_PARAMETERS,
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
