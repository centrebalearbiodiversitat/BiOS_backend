import csv
import re

from django.db.models import Count, Q
from django.db.models.functions import Substr, Lower
from django.http import StreamingHttpResponse
from unidecode import unidecode
from apps.taxonomy.serializers import SearchTaxonomicLevelSerializer, TaxonomicFilterSerializer
from drf_yasg import openapi
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_tracking.mixins import LoggingMixin
from apps.API.exceptions import CBBAPIException
from apps.taxonomy.models import Authorship, TaxonomicLevel
from apps.taxonomy.serializers import AuthorshipSerializer, BaseTaxonomicLevelSerializer, TaxonCompositionSerializer

from apps.versioning.serializers import OriginIdSerializer
from common.utils.serializers import get_paginated_response
from .forms import IdFieldForm, TaxonomicLevelChildrenForm, TaxonomicLevelForm
from .utils import taxon_checklist_to_csv, generate_csv_taxon_list2
from common.utils.utils import EchoWriter, PUNCTUATION_TRANSLATE, str_clean_up
from common.utils.forms import TaxonomyForm
from apps.tags.forms import IUCNDataForm, DirectiveForm, SystemForm, TaxonTagForm

from common.utils.custom_swag_schema import custom_swag_schema


MANUAL_PARAMETERS = [
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the taxon to search for",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"ancestor_id",
				openapi.IN_QUERY,
				description="Filter taxa by the ID of their ancestor",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				"rank",
				openapi.IN_QUERY,
				description="Filter taxa by their taxonomic rank",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"accepted",
				openapi.IN_QUERY,
				description="Filter by accepted/unaccepted taxonomic status",
				type=openapi.TYPE_BOOLEAN
			),
			openapi.Parameter(
				"has_image",
				openapi.IN_QUERY,
				description="Filter taxa with or without images",
				type=openapi.TYPE_BOOLEAN
			),
			openapi.Parameter(
				"source",
				openapi.IN_QUERY,
				description="Filter taxa by the source of information",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"tag",
				openapi.IN_QUERY,
				description="Filter taxa by a specific tag name",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"iucnGlobal",
				openapi.IN_QUERY,
				description="Filter taxa by IUCN status at Global level",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"iucnEurope",
				openapi.IN_QUERY,
				description="Filter taxa by IUCN status at Europe level",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"iucnMediterranean",
				openapi.IN_QUERY,
				description="Filter taxa by IUCN status at Mediterranean level",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"directive",
				openapi.IN_QUERY,
				description="Filter taxa by a specific directive",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"system",
				openapi.IN_QUERY,
				description="Filter taxa by a specific system",
				type=openapi.TYPE_STRING
			)
		]


class TaxonSearch:
	def search(self, request, limit=10):
		taxon_form = TaxonomicLevelForm(data=request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		filters = {}
		query = taxon_form.cleaned_data.get("name", None)
		exact = taxon_form.cleaned_data.get("exact", False)

		if not query:
			return []

		queryset = None
		query = unidecode(str_clean_up(query).translate(PUNCTUATION_TRANSLATE))
		for query in re.findall(r"(?:[x|X] \S+)|\S+", query):
			filters["name__istartswith"] = query
			if queryset is None:
				queryset = TaxonomicLevel.objects.annotate(prefix=Lower(Substr("unidecode_name", 1, min(3, len(query))))).filter(prefix=query[:3].lower()).filter(**filters)
			else:
				queryset = (
					TaxonomicLevel.objects.annotate(prefix=Lower(Substr("unidecode_name", 1, min(3, len(query)))))
					.filter(prefix=query[:3].lower())
					.filter(**filters, rank__in=[TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY], parent__in=queryset)
				)
		if not queryset:
			queryset = TaxonomicLevel.objects.none()

		if not exact and queryset.count() < limit:
			for instance in queryset.filter(rank__in=[TaxonomicLevel.GENUS, TaxonomicLevel.SPECIES])[:limit]:
				queryset |= instance.get_descendants()

		return queryset.distinct()


class TaxonFilter(TaxonSearch):
	def get_taxon_list(self, request):
		taxon_form = TaxonomicLevelForm(data=request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		query = TaxonomicLevel.objects.all()

		ancestor_id = taxon_form.cleaned_data.get("ancestor_id", False)
		if ancestor_id:
			try:
				query = TaxonomicLevel.objects.get(id=ancestor_id).get_descendants()
			except TaxonomicLevel.DoesNotExist:
				raise CBBAPIException("Ancestor id not found", code=404)

		rank = taxon_form.cleaned_data.get("rank", None)
		if rank:
			query = query.filter(rank=rank)

		accepted = taxon_form.cleaned_data.get("accepted", None)
		if accepted is not None:
			query = query.filter(accepted=accepted)

		has_image = taxon_form.cleaned_data.get("has_image", None)
		if has_image is not None:
			query = query.exclude(images__isnull=has_image)

		filters = Q()
		filtered_data = {}

		name = taxon_form.cleaned_data.get("name", None)
		if name:
			query = self.search(request).exclude(~Q(id__in=query))

		iucn_form = IUCNDataForm(data=request.GET)

		if not iucn_form.is_valid():     
			raise CBBAPIException(iucn_form.errors, 400)
		
		for key, value in iucn_form.cleaned_data.items():
			if value != "":
				filtered_data[f"iucndata__{key}"] = value

		directive_form = DirectiveForm(data=request.GET)

		if not directive_form.is_valid():
			raise CBBAPIException(directive_form.errors, 400)
		
		for key, value in directive_form.cleaned_data.items():
			if value:
				filtered_data[f"directive__{key}"] = value

		system_form = SystemForm(data=request.GET)

		if not system_form.is_valid():
			raise CBBAPIException(system_form.errors, 400)
		
		for key, value in system_form.cleaned_data.items():
			if value:
				filtered_data[f"system__{key}"] = value

		tag_form = TaxonTagForm(data=request.GET)

		if not tag_form.is_valid():
			raise CBBAPIException(tag_form.errors, 400)
		
		if tag_form.cleaned_data.get("tag", None):
			filtered_data["taxontag__tag__name__iexact"] = tag_form.cleaned_data.get("tag")

		for field, value in filtered_data.items():
			if value is not None:
				filters &= Q(**{field: value})

		source = taxon_form.cleaned_data.get("source", None)

		if source:
			filters &= Q(sources__source__basis__internal_name__icontains=source)
		query = query.filter(filters)

		return query


class TaxonSearchView(APIView, TaxonSearch):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Search taxon by name",
		operation_description="Search for a taxon by name.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the taxon to search for",
				type=openapi.TYPE_STRING,
				required=True,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match",
				type=openapi.TYPE_BOOLEAN,
				default=False
			)
		]
	)
	def get(self, request):
		return Response(SearchTaxonomicLevelSerializer(self.search(request)[:10], many=True).data)

class TaxonListView(APIView, TaxonFilter):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="List of taxa",
		operation_description="Get a list of the selected taxon and its children, if available, with optional filtering.",
		manual_parameters=MANUAL_PARAMETERS + [
			openapi.Parameter(
				"page",
				openapi.IN_QUERY,
				description="Number of page",
				type=openapi.TYPE_INTEGER
			)
		]
	)
	def get(self, request):
		return Response(get_paginated_response(request, self.get_taxon_list(request), TaxonomicFilterSerializer))


class TaxonCountView(LoggingMixin, APIView, TaxonFilter):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Count filtered taxa",
		operation_description="Get a count of taxa based on filters filters.",
		manual_parameters=MANUAL_PARAMETERS
	)
	def get(self, request):
		return Response(self.get_taxon_list(request).count())


# class TaxonSearchView(APIView, TaxonSearch):
# 	@custom_swag_schema(
# 		tags="Taxonomy",
# 		operation_id="Search taxon by name",
# 		operation_description="Retrieve basic information about a taxon using its scientific name.",
# 		manual_parameters=[
# 			openapi.Parameter(
# 				"name",
# 				openapi.IN_QUERY,
# 				description="Name of the taxon to search for",
# 				type=openapi.TYPE_STRING
# 			),
# 			openapi.Parameter(
# 				"exact",
# 				openapi.IN_QUERY,
# 				description="Indicates whether to search for an exact match",
# 				type=openapi.TYPE_BOOLEAN,
# 				default=False
# 			)
# 		]
# 	)
# 	def get(self, request):
# 		return Response(SearchTaxonomicLevelSerializer(self.search(request)[:10], many=True).data[0])

# TO DO: The result is identical to TaxonChecklistView. Can we insert just the id into the other endpoint?
class TaxonListCSVView(APIView, TaxonFilter):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Download taxon list (CSV)",
		operation_description="Get a list of taxa as a CSV file, with optional filtering.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the taxon to search for.",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"ancestor_id",
				openapi.IN_QUERY,
				description="Filter taxa by the ID of their ancestor.",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				"rank",
				openapi.IN_QUERY,
				description="Filter taxa by their taxonomic rank.",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				"accepted",
				openapi.IN_QUERY,
				description="Filter by accepted/unaccepted taxa.",
				type=openapi.TYPE_BOOLEAN
			),
			openapi.Parameter(
				"has_image",
				openapi.IN_QUERY,
				description="Filter taxa with or without images.",
				type=openapi.TYPE_BOOLEAN
			),
			openapi.Parameter(
				"source",
				openapi.IN_QUERY,
				description="Filter taxa by the source of information.",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"tag",
				openapi.IN_QUERY,
				description="Filter taxa by a specific tag name.",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				"iucnStatus",
				openapi.IN_QUERY,
				description="Filter taxa by IUCN status.",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				"directive",
				openapi.IN_QUERY,
				description="Filter taxa by a specific directive.",
				type=openapi.TYPE_BOOLEAN
			),
			openapi.Parameter(
				"system",
				openapi.IN_QUERY,
				description="Filter taxa by a specific system.",
				type=openapi.TYPE_BOOLEAN
			),
		]
	)
	def get(self, request):
		query = self.get_taxon_list(request)
		to_csv = generate_csv_taxon_list2(query)
		csv_writer = csv.writer(EchoWriter())

		return StreamingHttpResponse(
			(csv_writer.writerow(row) for row in to_csv),
			content_type="text/csv",
			headers={"Content-Disposition": f'attachment; filename="taxonomy_list.csv"'},
		)


class TaxonCRUDView(APIView):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Get taxon by id",
		operation_description="Retrieve a specific TaxonomicLevel instance by its id",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		]
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", code=404)

		return Response(BaseTaxonomicLevelSerializer(taxon).data)


class TaxonParentView(APIView):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Get parent taxon",
		operation_description="Get the parents of a taxon given its ID",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True
			)
		]
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, 400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", 400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		ancestors = taxon.get_ancestors()

		return Response(BaseTaxonomicLevelSerializer(ancestors, many=True).data)


class TaxonChildrenBaseView(APIView):
	def get(self, request):
		taxon_form = TaxonomicLevelChildrenForm(data=self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		filters = {}
		if taxon_form.cleaned_data.get("accepted_only") is True:
			filters["accepted"] = True

		children_rank = TaxonomicLevel.TRANSLATE_RANK.get(taxon_form.cleaned_data.get("children_rank", None), None)
		if children_rank:
			return taxon.get_descendants().filter(rank=children_rank).filter(**filters)
		else:
			return taxon.get_children().filter(**filters)


class TaxonChildrenView(TaxonChildrenBaseView):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Get taxon children",
		operation_description="Get the children of the given taxon id.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the taxonomic level",
				required=True,
			),
			openapi.Parameter(
				"childrenRank",
				openapi.IN_QUERY,
				type=openapi.TYPE_STRING,
				description="The level of children to look up for",
				required=False
			),
			openapi.Parameter(
				"accepted_only",
				openapi.IN_QUERY,
				type=openapi.TYPE_BOOLEAN,
				description="Filter to show only accepted children",
				required=False
			)
		]
	)
	def get(self, request):
		return Response(BaseTaxonomicLevelSerializer(super().get(request), many=True).data)


class TaxonChildrenCountView(LoggingMixin, TaxonChildrenBaseView):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Count taxon children",
		operation_description="Get the total count of children for the given taxon ID.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the taxonomic level",
				required=True
			),
			openapi.Parameter(
				"childrenRank",
				openapi.IN_QUERY,
				type=openapi.TYPE_STRING,
				description="The level of children to look up for",
				required=False
			),
			openapi.Parameter(
				"accepted_only",
				openapi.IN_QUERY,
				type=openapi.TYPE_BOOLEAN,
				description="Filter to count only accepted children",
				required=False
			)
		]
	)
	def get(self, request):
		return Response(super().get(request).count())


class TaxonSistersView(APIView):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Get taxon sisters",
		operation_description="Get the sisters of a given taxon by its ID.",
		manual_parameters=[
			openapi.Parameter(
				name="taxonomy",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="Taxon ID",
				required=True
			)
		]
	)
	def get(self, request, *args, **kwargs):
		taxon_form = TaxonomyForm(self.request.GET)
		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data["taxonomy"]

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		siblings = taxon.get_siblings(include_self=False)
		
		if siblings:
			return Response(BaseTaxonomicLevelSerializer(siblings, many=True).data)
		else:
			raise CBBAPIException("No sisters found for the given taxon.", code=200)


class TaxonomicLevelDescendantsCountView(APIView):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Count taxon descendants by rank",
		operation_description="Get the count of descendants of a taxonomic level, grouped by rank.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve its descendants count",
				type=openapi.TYPE_INTEGER,
				required=True
			)
		]
	)
	def get(self, request):
		taxon_data_form = TaxonomicLevelForm(data=request.GET)

		if not taxon_data_form.is_valid():
			raise CBBAPIException(taxon_data_form.errors, code=400)

		taxonomy = taxon_data_form.cleaned_data.get("id", None)
		try:
			taxon = TaxonomicLevel.objects.get(id=taxonomy)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("TaxonomicLevel not found", code=404)

		result = {}
		descendants = taxon.get_descendants(include_self=False).filter(accepted=True).values("rank").order_by("rank").annotate(count=Count("rank"))
		for descendant in descendants:
			result[TaxonomicLevel.TRANSLATE_RANK[descendant["rank"]]] = descendant["count"]

		return Response(result)


class TaxonSynonymView(ListAPIView):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Get taxon synonyms",
		operation_description="Get a list of synonyms for a given taxon by its ID.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="Taxon ID",
				type=openapi.TYPE_INTEGER,
				required=True
			)
		]
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		return Response(BaseTaxonomicLevelSerializer(taxon.synonyms, many=True).data)


class TaxonCompositionView(ListAPIView):
	@custom_swag_schema(
		tags="Taxonomy",
		operation_id="Get taxon composition",
		operation_description="Get the direct children of a taxon and the count of accepted species within each child.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		]
	)
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			children = TaxonomicLevel.objects.get(id=taxon_id).get_children().filter(accepted=True)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		for child in children:
			child.total_species = child.get_descendants(include_self=True).filter(rank=TaxonomicLevel.SPECIES, accepted=True).count()

		# species = TaxonomicLevel.objects.none()
		# species = children.annotate(
		# 	total_species=Subquery(
		# 		TaxonomicLevel.objects.filter(lft__gt=OuterRef('lft'), rght__lt=OuterRef('rght'))
		# 						.filter(rank=TaxonomicLevel.SPECIES, accepted=True)
		# 						.annotate(base_parent=Count('id'))
		# 						.values('base_parent')
		# 						.annotate(total_species=Count('id'))
		# 						.values("total_species")
		# 	)
		# )

		return Response(TaxonCompositionSerializer(children, many=True).data)


class TaxonSourceView(ListAPIView):
	@custom_swag_schema(
        tags="Taxonomy",
        operation_id="Get taxon sources",
        operation_description="Get a list of sources associated with a given taxon by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the taxon to retrieve its sources",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, 400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)
		return Response(OriginIdSerializer(taxon.sources, many=True).data)


class TaxonChecklistView(APIView):
	@custom_swag_schema(
        tags="Taxonomy",
        operation_id="Download taxon checklist (CSV)",
        operation_description="Get a checklist of a taxonomic level and its accepted children in CSV format.",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the taxon to retrieve all its accepted children for the checklist",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
	def get(self, request):
		taxon_form = TaxonomicLevelForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			head_taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", code=404)

		to_csv = taxon_checklist_to_csv(head_taxon)

		csv_writer = csv.writer(EchoWriter())

		return StreamingHttpResponse(
			(csv_writer.writerow(row) for row in to_csv),
			content_type="text/csv",
			headers={"Content-Disposition": f'attachment; filename="{head_taxon}_checklist.csv"'},
		)


class AuthorshipCRUDView(APIView):
	@custom_swag_schema(
        tags="Authorship",
        operation_id="Get authorship by id",
        operation_description="Get authorship information by its ID.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Authorship ID",
                required=True
            )
        ]
    )
	def get(self, request):
		authorship_form = IdFieldForm(self.request.GET)

		if not authorship_form.is_valid():
			raise CBBAPIException(authorship_form.errors, code=400)

		authorship_id = authorship_form.cleaned_data.get("id")

		if not authorship_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			authorship = Authorship.objects.get(id=authorship_id)
		except Authorship.DoesNotExist:
			raise CBBAPIException("Authorship does not exist.", code=404)

		return Response(AuthorshipSerializer(authorship).data)
