import csv
import re

from django.db.models import Count, Q
from django.db.models.functions import Substr, Lower
from django.http import StreamingHttpResponse
from unidecode import unidecode
from apps.taxonomy.serializers import SearchTaxonomicLevelSerializer, AncestorsTaxonomicLevelSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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


class TaxonSearchView(APIView, TaxonSearch):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Search for a taxon by name.",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the taxon to search for.",
				type=openapi.TYPE_STRING,
				required=True,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(SearchTaxonomicLevelSerializer(self.search(request)[:10], many=True).data)


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
				filtered_data[f"iucndata__{key}"] = value and int(value)

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


class TaxonListView(APIView, TaxonFilter):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of taxa, with optional filtering.",
		manual_parameters=[
			openapi.Parameter("name", openapi.IN_QUERY, description="Name of the taxon to search for.", type=openapi.TYPE_STRING),
			openapi.Parameter(
				"taxonRank",
				openapi.IN_QUERY,
				description="Rank id of the taxon to search for.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"scientificNameAuthorship",
				openapi.IN_QUERY,
				description="Authorship id of the taxon to search for.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"parent",
				openapi.IN_QUERY,
				description="Parent id of the taxon to search for.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(get_paginated_response(request, self.get_taxon_list(request), AncestorsTaxonomicLevelSerializer))


class TaxonListCSVView(APIView, TaxonFilter):
	def get(self, request):
		query = self.get_taxon_list(request)

		to_csv = generate_csv_taxon_list2(query)

		csv_writer = csv.writer(EchoWriter())

		return StreamingHttpResponse(
			(csv_writer.writerow(row) for row in to_csv),
			content_type="text/csv",
			headers={"Content-Disposition": f'attachment; filename="list.csv"'},
		)


class TaxonCountView(LoggingMixin, APIView, TaxonFilter):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of taxa, with optional filtering.",
		manual_parameters=[
			openapi.Parameter("name", openapi.IN_QUERY, description="Name of the taxon to search for.", type=openapi.TYPE_STRING),
			openapi.Parameter(
				"taxonRank",
				openapi.IN_QUERY,
				description="Rank id of the taxon to search for.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"scientificNameAuthorship",
				openapi.IN_QUERY,
				description="Authorship id of the taxon to search for.",
				type=openapi.TYPE_STRING,
			),
			openapi.Parameter(
				"parent",
				openapi.IN_QUERY,
				description="Parent id of the taxon to search for.",
				type=openapi.TYPE_INTEGER,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(self.get_taxon_list(request).count())


class TaxonCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Retrieve a specific TaxonomicLevel instance by its id",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the parents of the taxon given its ID",
		manual_parameters=[
			openapi.Parameter(name="id", in_=openapi.IN_QUERY, description="ID of the taxon", type=openapi.TYPE_INTEGER, required=True),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the children of the given taxon id",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the taxonomic level",
				required=True,
			),
			openapi.Parameter(
				name="childrenRank",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="The level of children to look up for",
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(BaseTaxonomicLevelSerializer(super().get(request), many=True).data)


class TaxonChildrenCountView(LoggingMixin, TaxonChildrenBaseView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the total children of the given taxon id",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the taxonomic level",
				required=True,
			),
			openapi.Parameter(
				name="childrenRank",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="The level of children to look up for",
				required=False,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		return Response(super().get(request).count())


class TaxonSistersView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the sisters of the given taxon id",
		manual_parameters=[
			openapi.Parameter(
				name="taxonomy",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the taxonomic level",
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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

		return Response(BaseTaxonomicLevelSerializer(siblings, many=True).data)


class TaxonomicLevelDescendantsCountView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the count of descendants of a taxonomic level by it's ID.",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				description="ID of the taxon to retrieve it's descendants",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of taxa, with optional filtering.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve its synonym",
				type=openapi.TYPE_STRING,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the children and the quantity of species for each.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon",
				type=openapi.TYPE_STRING,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of sources, with optional filtering.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve its sources",
				type=openapi.TYPE_STRING,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a checklist of a taxonomic level.",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve all its childrens",
				type=openapi.TYPE_INTEGER,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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
	@swagger_auto_schema(
		tags=["Authorship"],
		operation_description="Get authorship info by ID",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the authorship",
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
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
