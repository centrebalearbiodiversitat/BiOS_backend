from django.db.models import Q, Count, Case, F, When, Value
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.taxonomy.models import TaxonomicLevel
from apps.API.exceptions import CBBAPIException
from .forms import OccurrenceForm
from .models import Occurrence
from .serializers import (
	OccurrenceSerializer,
	BaseOccurrenceSerializer,
	DownloadOccurrenceSerializer,
	OccurrenceCountByDateSerializer,
	DynamicSourceSerializer,
)
from apps.geography.models import GeographicLevel
from apps.tags.forms import IUCNDataForm, DirectiveForm, SystemForm, TaxonTagForm
from common.utils.views import CSVDownloadMixin


class OccurrenceCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Get occurrence by ID",
		operation_description="Get details of a specific Occurrence.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Occurrence ID",
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

		print(f'MIN_VALUE: {min_value} ---- MAX_VALUE: {max_value}')

		if min_value:
			print(f'{min_value}')
			filters &= Q(**{f"{field_name}__gte": min_value})
		if max_value:
			print(f'{max_value}')
			filters &= Q(**{f"{field_name}__lte": max_value})

		print(f'---- {filters} ----')
		return filters

	def calculate(self, request, in_geography_scope=True):

		# print(request.GET)
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		taxonomy = occur_form.cleaned_data.get("taxonomy", None)
		add_synonyms = occur_form.cleaned_data.get("add_synonyms")

		filters = Q()

		if taxonomy:
			taxon_query = Q(id=taxonomy)
			if add_synonyms:
				taxon_query |= Q(synonyms=taxonomy, accepted=True)
			taxa = TaxonomicLevel.objects.filter(taxon_query).distinct()

			if not taxa:
				raise CBBAPIException("Taxonomic level does not exist", 404)

			for taxon in taxa:
				filters |= Q(taxonomy__id=taxon.id) | Q(taxonomy__lft__gte=taxon.lft, taxonomy__rght__lte=taxon.rght)

		filtered_data = {}

		iucn_form = IUCNDataForm(data=request.GET)
		if not iucn_form.is_valid():
			raise CBBAPIException(iucn_form.errors, 400)
		for key, value in iucn_form.cleaned_data.items():
			if value != "":
				filtered_data[f"taxonomy__iucndata__{key}"] = value and int(value)

		directive_form = DirectiveForm(data=request.GET)
		if not directive_form.is_valid():
			raise CBBAPIException(directive_form.errors, 400)
		for key, value in directive_form.cleaned_data.items():
			if value:
				filtered_data[f"taxonomy__directive__{key}"] = value

		system_form = SystemForm(data=request.GET)
		if not system_form.is_valid():
			raise CBBAPIException(system_form.errors, 400)
		for key, value in system_form.cleaned_data.items():
			if value:
				filtered_data[f"taxonomy__system__{key}"] = value

		tag_form = TaxonTagForm(data=request.GET)
		if not tag_form.is_valid():
			raise CBBAPIException(tag_form.errors, 400)
		if tag_form.cleaned_data.get("tag"):
			filtered_data["taxonomy__taxontag__tag__name__iexact"] = tag_form.cleaned_data.get("tag")

		for field, value in filtered_data.items():
			if value is not None:
				filters &= Q(**{field: value})

		source = occur_form.cleaned_data.get("source", None)
		if source:
			filters &= Q(sources__source__basis__internal_name__icontains=source)

		voucher = occur_form.cleaned_data.get("voucher", None)
		if voucher:
			filters &= Q(voucher__icontains=voucher)

		has_sequence = occur_form.cleaned_data.get("has_sequence", None)
		if has_sequence is not None:
			filters &= Q(sequence__isnull=not has_sequence)

		# Design the coordinate filtering system

		range_parameters_direct = ["coordinate_uncertainty_in_meters", "elevation", "depth", "collection_date_year"]

		print(occur_form.cleaned_data)

		for param in range_parameters_direct:
			print(f'{param}\n')
			filters = self.filter_by_range(
				filters,
				param,
				occur_form.cleaned_data.get(f"{param}_min"),
				occur_form.cleaned_data.get(f"{param}_max"),
			)
			print(f'{filters}\n')

		occurrences = Occurrence.objects.filter(filters).distinct()

		gl = occur_form.cleaned_data.get("geographical_location", None)
		if gl:
			try:
				gl = GeographicLevel.objects.get(id=gl)
				occurrences = occurrences.filter(location__within=gl.area)
			except GeographicLevel.DoesNotExist:
				raise CBBAPIException("Geographical location does not exist", 404)

		if in_geography_scope:
			occurrences = occurrences.filter(in_geography_scope=in_geography_scope)

		return occurrences


class OccurrenceMapView(OccurrenceFilter):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Get occurrence map",
		operation_description="Filter occurrences based on query parameters.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by taxon id.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"voucher",
				openapi.IN_QUERY,
				description="Filter occurrences by voucher field.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"geographicalLocation",
				openapi.IN_QUERY,
				description="Filter occurrences by geographical location id.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"year",
				openapi.IN_QUERY,
				description="Filter occurrences by year field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"month",
				openapi.IN_QUERY,
				description="Filter occurrences by month field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"day",
				openapi.IN_QUERY,
				description="Filter occurrences by day field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"basisOfRecord",
				openapi.IN_QUERY,
				description="Filter occurrences by basis of record field.",
				type=openapi.TYPE_STRING,
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
		return Response(BaseOccurrenceSerializer(self.calculate(request).distinct("location"), many=True).data)


class OccurrenceMapCountView(OccurrenceFilter):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Get occurrence map count",
		operation_description="Filter occurrences based on query parameters.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by taxon id.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"voucher",
				openapi.IN_QUERY,
				description="Filter occurrences by voucher field.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"geographicalLocation",
				openapi.IN_QUERY,
				description="Filter occurrences by geographical location id.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"year",
				openapi.IN_QUERY,
				description="Filter occurrences by year field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"month",
				openapi.IN_QUERY,
				description="Filter occurrences by month field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"day",
				openapi.IN_QUERY,
				description="Filter occurrences by day field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"basisOfRecord",
				openapi.IN_QUERY,
				description="Filter occurrences by basis of record field.",
				type=openapi.TYPE_STRING,
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
		return Response(self.calculate(request).distinct("location").count())


class OccurrenceListView(OccurrenceFilter):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Get filtered occurrences",
		operation_description="Filter occurrences based on query parameters.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"voucher",
				openapi.IN_QUERY,
				description="Voucher ID",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"geographicalLocation", # ???
				openapi.IN_QUERY,
				description="Filter occurrences by geographical location id.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"month",
				openapi.IN_QUERY,
				description="Filter occurrences by month field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"day",
				openapi.IN_QUERY,
				description="Filter occurrences by day field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"basisOfRecord", # We need to use the basisOfRecord id, maybe we need a endpoint to list the basisOfRecord with the IDs
				openapi.IN_QUERY,
				description="Filter occurrences by basis of record field.",
				type=openapi.TYPE_STRING,
			),
			# openapi.Parameter(
			# 	"decimal_latitude_min",
			# 	openapi.IN_QUERY,
			# 	description="Minimum latitude",
			# 	type=openapi.TYPE_NUMBER,
			# 	format=openapi.FORMAT_DECIMAL,
			# ),
			# openapi.Parameter(
			# 	"decimal_latitude_max",
			# 	openapi.IN_QUERY,
			# 	description="Maximum latitude",
			# 	type=openapi.TYPE_NUMBER,
			# 	format=openapi.FORMAT_DECIMAL,
			# ),
			# openapi.Parameter(
			# 	"decimal_longitude_min",
			# 	openapi.IN_QUERY,
			# 	description="Minimum longitude",
			# 	type=openapi.TYPE_NUMBER,
			# 	format=openapi.FORMAT_DECIMAL,
			# ),
			# openapi.Parameter(
			# 	"decimal_longitude_max",
			# 	openapi.IN_QUERY,
			# 	description="Maximum longitude",
			# 	type=openapi.TYPE_NUMBER,
			# 	format=openapi.FORMAT_DECIMAL,
			# ),
			openapi.Parameter(
				"collection_date_year_min",
				openapi.IN_QUERY,
				description="Filter occurrences by year field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"collection_date_year_max",
				openapi.IN_QUERY,
				description="Filter occurrences by year field.",
				type=openapi.TYPE_INTEGER,
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
			openapi.Parameter(
				"elevation_min",
				openapi.IN_QUERY,
				description="Minimum elevation",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				"elevation_max",
				openapi.IN_QUERY,
				description="Maximum elevation",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				"depth_min",
				openapi.IN_QUERY,
				description="Minimum depth",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				"depth_max",
				openapi.IN_QUERY,
				description="Maximum depth",
				type=openapi.TYPE_INTEGER
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		# return Response(BaseOccurrenceSerializer(self.calculate(request), many=True).data)
		return Response(OccurrenceSerializer(self.calculate(request), many=True).data)


class OccurrenceListDownloadView(OccurrenceFilter):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Download occurrences (CSV)",
		operation_description="Download filtered occurrences as a CSV file.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by taxon id.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"voucher",
				openapi.IN_QUERY,
				description="Filter occurrences by voucher field.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"geographicalLocation",
				openapi.IN_QUERY,
				description="Filter occurrences by geographical location id.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"year",
				openapi.IN_QUERY,
				description="Filter occurrences by year field.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"month",
				openapi.IN_QUERY,
				description="Filter occurrences by month field.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"day",
				openapi.IN_QUERY,
				description="Filter occurrences by day field.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"basisOfRecord",
				openapi.IN_QUERY,
				description="Filter occurrences by basis of record field.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"decimal_latitude_min",
				openapi.IN_QUERY,
				description="Minimum latitude",
				type=openapi.TYPE_NUMBER,
				format=openapi.FORMAT_DECIMAL,
				required=False,
			),
			openapi.Parameter(
				"decimal_latitude_max",
				openapi.IN_QUERY,
				description="Maximum latitude",
				type=openapi.TYPE_NUMBER,
				format=openapi.FORMAT_DECIMAL,
				required=False,
			),
			openapi.Parameter(
				"decimal_longitude_min",
				openapi.IN_QUERY,
				description="Minimum longitude",
				type=openapi.TYPE_NUMBER,
				format=openapi.FORMAT_DECIMAL,
				required=False,
			),
			openapi.Parameter(
				"decimal_longitude_max",
				openapi.IN_QUERY,
				description="Maximum longitude",
				type=openapi.TYPE_NUMBER,
				format=openapi.FORMAT_DECIMAL,
				required=False,
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
	)

	def get(self, request):
		response = self.calculate(request)
		flattened_data = CSVDownloadMixin.flatten_json(DownloadOccurrenceSerializer(response, many=True).data, ["sources"])

		return CSVDownloadMixin.generate_csv(flattened_data, "occurrences.csv")


class OccurrenceCountView(OccurrenceFilter):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Count filtered occurrences",
		operation_description="Counts the filtered occurrences based on the provided query parameters.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by taxon id.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"voucher",
				openapi.IN_QUERY,
				description="Filter occurrences by voucher field.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"geographicalLocation",
				openapi.IN_QUERY,
				description="Filter occurrences by geographical location id.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"year",
				openapi.IN_QUERY,
				description="Filter occurrences by year field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"month",
				openapi.IN_QUERY,
				description="Filter occurrences by month field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"day",
				openapi.IN_QUERY,
				description="Filter occurrences by day field.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"basisOfRecord",
				openapi.IN_QUERY,
				description="Filter occurrences by basis of record field.",
				type=openapi.TYPE_STRING,
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
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(self.calculate(request).count())


class OccurrenceCountBySourceView(APIView):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Count occurrences by source",
		operation_description="Get counts of occurrences grouped by source.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		taxonomy = occur_form.cleaned_data.get("taxonomy", None)
		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)

		try:
			taxonomy = TaxonomicLevel.objects.get(id=taxonomy).get_descendants(include_self=True)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		occurrences = (
			Occurrence.objects.filter(taxonomy__in=taxonomy, in_geography_scope=True)
			.prefetch_related("sources")
			.values("sources__source__basis__internal_name")
			.annotate(count=Count("id"))
			.order_by("sources__source__basis__internal_name")
		)

		return Response(DynamicSourceSerializer(occurrences, many=True).data)


class OccurrenceCountByTaxonAndChildrenView(APIView):
	def check_ancestors(self, children_id, parents_list, count):
		taxon_children = TaxonomicLevel.objects.get(id=children_id)
		ancestors = taxon_children.get_ancestors()

		for parent in parents_list:
			if ancestors.filter(id=parent.id).exists():
				ancestor = ancestors.get(id=parent.id)
				context = {
					"taxonomy": ancestor.name,
					"count": count,
				}
				return context
			
	@swagger_auto_schema(
		 tags=["Occurrences"],
		operation_id="Count occurrences by taxon children",
		operation_description="Get count of occurrence grouped by the children of a taxon according to its ID.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by Taxon ID",
				type=openapi.TYPE_INTEGER,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)

		taxonomy = occur_form.cleaned_data.get("taxonomy", None)
		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)
		

		try:
			taxon_parent = TaxonomicLevel.objects.get(id=taxonomy)
			if taxon_parent.rank >= 6:
				raise CBBAPIException(
					f"{TaxonomicLevel.TRANSLATE_RANK[taxon_parent.rank].upper()} is not valid for children stats, try genus or greater taxonomic levels",
					400
				)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)
		childrens = taxon_parent.get_children()
		descendants = taxon_parent.get_descendants(include_self=True)

		annotated_occ = (
			Occurrence.objects.annotate(
				descendant_taxonomy=Case(When(taxonomy__in=descendants, then=F("taxonomy__name")), default=Value("Unknown")),
				descendant_taxon_id=Case(When(taxonomy__in=descendants, then=F("taxonomy__id")), default=None),
			)
			.values("descendant_taxonomy", "descendant_taxon_id")
			.annotate(count=Count("id"))
			.order_by("descendant_taxonomy")
		)

		response = []
		for i in annotated_occ:
			ancestor = self.check_ancestors(i["descendant_taxon_id"], childrens, i["count"])
			response.append(ancestor)

		return JsonResponse(response, safe=False)


# class OccurrenceCountByTaxonDateBaseView:
# 	def calculate(self, request, date_key, view_class):
# 		occur_form = OccurrenceForm(data=request.GET)

# 		if not occur_form.is_valid():
# 			raise CBBAPIException(occur_form.errors, 400)

# 		taxonomy = occur_form.cleaned_data.get("taxonomy", None)
# 		if not taxonomy:
# 			raise CBBAPIException("Missing taxonomy id parameter", 400)

# 		try:
# 			taxonomy = TaxonomicLevel.objects.get(id=taxonomy).get_descendants(include_self=True)
# 		except TaxonomicLevel.DoesNotExist:
# 			raise CBBAPIException("Taxonomic level does not exist", 404)

# 		occurrences = Occurrence.objects.filter(taxonomy__in=taxonomy, in_geography_scope=True).values(date_key).annotate(count=Count("id")).order_by(date_key)

# 		return Response(OccurrenceCountByDateSerializer(occurrences, many=True, view_class=view_class).data)


# class OccurrenceCountByTaxonMonthView(APIView, OccurrenceCountByTaxonDateBaseView):
# 	@swagger_auto_schema(
# 		tags=["Occurrences"],
# 		operation_description="Get counts of occurrences grouped by month for a given Taxon ID.",
# 		manual_parameters=[
# 			openapi.Parameter(
# 				"taxonomy",
# 				openapi.IN_QUERY,
# 				description="Filter occurrences by Taxon ID",
# 				type=openapi.TYPE_INTEGER,
# 			),
# 		],
# 		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
# 	)
# 	def get(self, request):
# 		return self.calculate(request, "collection_date_month", self.__class__)


# class OccurrenceCountByTaxonYearView(APIView, OccurrenceCountByTaxonDateBaseView):
# 	@swagger_auto_schema(
# 		tags=["Occurrences"],
# 		operation_description="Get counts of occurrences grouped by year for a given Taxon ID.",
# 		manual_parameters=[
# 			openapi.Parameter(
# 				"taxonomy",
# 				openapi.IN_QUERY,
# 				description="Filter occurrences by Taxon ID",
# 				type=openapi.TYPE_INTEGER,
# 			),
# 		],
# 		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
# 	)
# 	def get(self, request):
# 		return self.calculate(request, "collection_date_year", self.__class__)

class OccurrenceCountByTaxonDateBaseView:
	def get_occurrences_by_taxonomy(self, taxonomy):		

		try:
			taxonomy = TaxonomicLevel.objects.get(id=taxonomy).get_descendants(include_self=True)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)
		
		return Occurrence.objects.filter(taxonomy__in=taxonomy, in_geography_scope=True)
		
	def get_occurrence_counts_by_month(self, occurrences):
		annotated_counts = (
			occurrences.values('collection_date_month')
			.annotate(count=Count('id'))
			.order_by('collection_date_month')
		)
		counts_dict = {
			item['collection_date_month']: item['count']
			for item in annotated_counts
		}
		months = {month: 0 for month in range(1, 13)}
		months.update(counts_dict)
		result = [{"month": month, "count": count} for month, count in months.items()]

		return result

	def get_occurrence_counts_by_year(self, occurrences):
		min_year = occurrences.order_by('collection_date_year').first().collection_date_year if occurrences.exists() else None
		max_year = occurrences.exclude(collection_date_year=None).order_by('-collection_date_year').first().collection_date_year if occurrences.exists() else None

		if not min_year or not max_year:
			return []

		all_years = list(range(min_year, max_year + 1))

		annotated_counts = (
			occurrences.values('collection_date_year')
			.annotate(count=Count('id'))
			.order_by('collection_date_year')
		)

		counts_dict = {
			item['collection_date_year']: item['count']
			for item in annotated_counts
		}

		response = []
		for year in all_years:
			count = counts_dict.get(year, 0)
			response.append({"count": count, "year": year})

		return response
	
	def calculate(self, request, date_key, view_class):
		occur_form = OccurrenceForm(data=request.GET)

		if not occur_form.is_valid():
			raise CBBAPIException(occur_form.errors, 400)
		
		taxonomy = occur_form.cleaned_data.get("taxonomy", None)

		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)
	
		occurrences = self.get_occurrences_by_taxonomy(taxonomy)

		if date_key == "collection_date_month":
			result = self.get_occurrence_counts_by_month(occurrences)
		elif date_key == "collection_date_year":
			result = self.get_occurrence_counts_by_year(occurrences)
		else:
			raise CBBAPIException("Invalid date_key", 400)

		return Response(OccurrenceCountByDateSerializer(result, many=True, view_class=view_class).data)


class OccurrenceCountByTaxonMonthView(APIView, OccurrenceCountByTaxonDateBaseView):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Count occurrences by taxon and month",
		operation_description="Get counts of occurrences grouped by month for a given Taxon ID.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by Taxon ID",
				type=openapi.TYPE_INTEGER,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return self.calculate(request, "collection_date_month", self.__class__)


class OccurrenceCountByTaxonYearView(APIView, OccurrenceCountByTaxonDateBaseView):
	@swagger_auto_schema(
		tags=["Occurrences"],
		operation_id="Count occurrences by taxon and year",
		operation_description="Get counts of occurrences grouped by year for a given Taxon ID.",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="Filter occurrences by Taxon ID",
				type=openapi.TYPE_INTEGER,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return self.calculate(request, "collection_date_year", self.__class__)
