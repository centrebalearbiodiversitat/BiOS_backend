import csv

from django.db.models import Count, Q, F, Subquery, OuterRef
from django.db.models.functions import Substr, Lower
from django.http import StreamingHttpResponse
from unidecode import unidecode

from apps.taxonomy.serializers import (
	SearchTaxonomicLevelSerializer,
	BaseTaxonDataSerializer,
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.API.exceptions import CBBAPIException
from apps.taxonomy.models import Authorship, TaxonData, TaxonomicLevel
from apps.taxonomy.serializers import AuthorshipSerializer, BaseTaxonomicLevelSerializer, TaxonCompositionSerializer, TaxonDataSerializer

from ..versioning.serializers import OriginSourceSerializer
from .forms import IdFieldForm, TaxonDataForm, TaxonomicLevelChildrenForm, TaxonomicLevelForm
from common.utils.utils import EchoWriter, PUNCTUATION_TRANSLATE, str_clean_up


class TaxonSearchView(APIView):
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
		taxon_form = TaxonomicLevelForm(data=self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		filters = {}
		query = taxon_form.cleaned_data.get("name", None)
		exact = taxon_form.cleaned_data.get("exact", False)
		limit = 10

		if not query:
			raise CBBAPIException("Missing name parameter", code=400)

		queryset = None
		query = unidecode(str_clean_up(query).translate(PUNCTUATION_TRANSLATE))

		for query in query.split(" "):
			filters["name__istartswith"] = query
			if queryset:
				queryset = (
					TaxonomicLevel.objects.annotate(prefix=Lower(Substr("unidecode_name", 1, min(3, len(query)))))
					.filter(prefix=query[:3].lower())
					.filter(
						**filters, rank__in=[TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY], parent__in=queryset
					)
				)
			else:
				queryset = (
					TaxonomicLevel.objects.annotate(prefix=Lower(Substr("unidecode_name", 1, min(3, len(query)))))
					.filter(prefix=query[:3].lower())
					.filter(**filters)
				)

		if not exact and queryset.count() < limit:
			for instance in queryset.filter(rank__in=[TaxonomicLevel.GENUS, TaxonomicLevel.SPECIES])[:limit]:
				queryset |= instance.get_descendants()

		return Response(SearchTaxonomicLevelSerializer(queryset.distinct()[:limit], many=True).data)


class TaxonFilter(ListAPIView):
	def get(self, request):
		taxon_form = TaxonomicLevelForm(data=request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)
		exact = taxon_form.cleaned_data.get("exact", False)
		str_fields = ["name"]

		filters = {}
		for param in taxon_form.cleaned_data:
			if param != "exact":
				if param in str_fields:
					value = taxon_form.cleaned_data.get(param)

					if value:
						param = f"{param}__iexact" if exact else f"{param}__icontains"
						filters[param] = value
				else:
					value = taxon_form.cleaned_data.get(param)
					if value or isinstance(value, int) or isinstance(value, bool):
						filters[param] = value

		if filters:
			query = TaxonomicLevel.objects.filter(**filters)
		else:
			query = TaxonomicLevel.objects.none()

		if not query.exists():
			raise CBBAPIException("No taxonomic levels found for the given filters.", 404)

		return query


class TaxonListView(TaxonFilter):
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
		return Response(BaseTaxonomicLevelSerializer(super().get(request), many=True).data)


class TaxonCountView(TaxonFilter):
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
		return Response(super().get(request).count())


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
		children_rank = TaxonomicLevel.TRANSLATE_RANK.get(taxon_form.cleaned_data.get("children_rank", None), None)

		if children_rank:
			filters["rank"] = children_rank

		if taxon_form.cleaned_data.get("accepted_only") is True:
			filters["accepted"] = True

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


class TaxonChildrenCountView(TaxonChildrenBaseView):
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
		taxon_form = self.request.GET

		taxon_id = taxon_form.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		return Response(OriginSourceSerializer(taxon.sources, many=True).data)


def map_taxa_to_rank(ranks, taxa):
	taxa_iter = iter(taxa)

	mapped_taxa = []
	current = next(taxa_iter, None)
	current_name = ""
	for rank in ranks:
		if current is None:
			break

		if rank == current.rank:
			if current.rank in [TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY]:
				current_name = f"{current_name} {current.name}"
			else:
				current_name = current.name

			mapped_taxa.append(current_name)
			mapped_taxa.append(current.verbatim_authorship)
			current = next(taxa_iter, None)
		else:
			mapped_taxa.append(None)
			mapped_taxa.append(None)

	return mapped_taxa


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

		ranks = [rank[1] for rank in TaxonomicLevel.RANK_CHOICES]
		ranks_map = [rank[0] for rank in TaxonomicLevel.RANK_CHOICES]
		to_csv = [
			[
				"id",
				"taxon",
				"status",
				"taxonRank",
				*list(sum([(f"{rank.lower()}", f"authorship{rank}") for rank in ranks], ())),
			]
		]

		upper_taxon = head_taxon.get_ancestors(include_self=False)  # .exclude(name__iexact='Biota')
		upper_taxon = list(upper_taxon)
		checklist = head_taxon.get_descendants(include_self=True)
		current_taxon = []
		last_level = -1
		for taxon in checklist:
			if last_level >= taxon.level:
				current_taxon = current_taxon[: len(current_taxon) - (last_level - taxon.level + 1)]

			current_taxon.append(taxon)
			taxa_map = map_taxa_to_rank(ranks_map, upper_taxon + current_taxon)
			to_csv.append([taxon.id, taxa_map[-2], taxon.readable_status(), taxon.readable_rank(), *taxa_map])
			last_level = taxon.level

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


class TaxonDataCRUDView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Retrieve a specific taxonomic data instance by its id",
		manual_parameters=[
			openapi.Parameter(
				"id",
				openapi.IN_QUERY,
				description="ID of the taxon data to retrieve",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = TaxonDataForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("id")

		if not taxon_id:
			raise CBBAPIException("Missing id parameter", code=400)

		try:
			taxon = TaxonData.objects.get(taxonomy=taxon_id)
		except TaxonData.DoesNotExist:
			raise CBBAPIException("Taxonomic data does not exist", code=404)

		return Response(TaxonDataSerializer(taxon).data)
  

class TaxonDataFilter:

	def get(self, request):
		taxon_data_form = TaxonDataForm(data=request.GET)

		if not taxon_data_form.is_valid():
			raise CBBAPIException(taxon_data_form.errors, code=400)

		exact = taxon_data_form.cleaned_data.get("exact", False)
		str_fields = ["habitat"]

		filters = {}
		for param in taxon_data_form.cleaned_data:
			if param != "exact":
				if param in str_fields:
					value = taxon_data_form.cleaned_data.get(param)

					if value:
						param = f"{param}__iexact" if exact else f"{param}__icontains"
						filters[param] = value
				else:
					value = taxon_data_form.cleaned_data.get(param)
					if value or isinstance(value, int):
						filters[param] = value

		if filters:
			query = TaxonData.objects.filter(**filters)
		else:
			query = TaxonData.objects.none()

		return query


class TaxonDataListView(TaxonDataFilter, ListAPIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of taxon data with filtering.",
		manual_parameters=[
			openapi.Parameter("taxonomy_id", openapi.IN_QUERY, description="ID of the taxon", type=openapi.TYPE_INTEGER),
			openapi.Parameter(
				"iucn_global",
				openapi.IN_QUERY,
				description="IUCN Global status",
				type=openapi.TYPE_STRING,
				enum=[str(c[0]) for c in TaxonData.CS_CHOICES],
			),
			openapi.Parameter(
				"iucn_europe",
				openapi.IN_QUERY,
				description="IUCN Europe status",
				type=openapi.TYPE_STRING,
				enum=[str(c[0]) for c in TaxonData.CS_CHOICES],
			),
			openapi.Parameter(
				"iucn_mediterranean",
				openapi.IN_QUERY,
				description="IUCN Mediterranean status",
				type=openapi.TYPE_STRING,
				enum=[str(c[0]) for c in TaxonData.CS_CHOICES],
			),
			openapi.Parameter("invasive", openapi.IN_QUERY, description="Is invasive?", type=openapi.TYPE_BOOLEAN),
			openapi.Parameter("domesticated", openapi.IN_QUERY, description="Is domesticated?", type=openapi.TYPE_BOOLEAN),
			openapi.Parameter("freshwater", openapi.IN_QUERY, description="Inhabit freshwater?", type=openapi.TYPE_BOOLEAN),
			openapi.Parameter("marine", openapi.IN_QUERY, description="Inhabit marine?", type=openapi.TYPE_BOOLEAN),
			openapi.Parameter("terrestrial", openapi.IN_QUERY, description="Inhabit terrestrial?", type=openapi.TYPE_BOOLEAN),
		],
		responses={200: "Success", 400: "Bad Request"},
	)
	def get(self, request):
		return Response(TaxonDataSerializer(super().get(request), many=True).data)


class TaxonDataCountView(TaxonDataFilter, ListAPIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get a list of taxon data with filtering.",
		manual_parameters=[
			openapi.Parameter("taxonomy_id", openapi.IN_QUERY, description="ID of the taxon", type=openapi.TYPE_INTEGER),
			openapi.Parameter(
				"iucn_global",
				openapi.IN_QUERY,
				description="IUCN Global status",
				type=openapi.TYPE_STRING,
				enum=[str(c[0]) for c in TaxonData.CS_CHOICES],
			),
			openapi.Parameter(
				"iucn_europe",
				openapi.IN_QUERY,
				description="IUCN Europe status",
				type=openapi.TYPE_STRING,
				enum=[str(c[0]) for c in TaxonData.CS_CHOICES],
			),
			openapi.Parameter(
				"iucn_mediterranean",
				openapi.IN_QUERY,
				description="IUCN Mediterranean status",
				type=openapi.TYPE_STRING,
				enum=[str(c[0]) for c in TaxonData.CS_CHOICES],
			),
			openapi.Parameter("invasive", openapi.IN_QUERY, description="Is invasive?", type=openapi.TYPE_BOOLEAN),
			openapi.Parameter("domesticated", openapi.IN_QUERY, description="Is domesticated?", type=openapi.TYPE_BOOLEAN),
			openapi.Parameter("freshwater", openapi.IN_QUERY, description="Inhabit freshwater?", type=openapi.TYPE_BOOLEAN),
			openapi.Parameter("marine", openapi.IN_QUERY, description="Inhabit marine?", type=openapi.TYPE_BOOLEAN),
			openapi.Parameter("terrestrial", openapi.IN_QUERY, description="Inhabit terrestrial?", type=openapi.TYPE_BOOLEAN),
		],
		responses={200: "Success", 400: "Bad Request"},
	)
	def get(self, request):
		return Response(super().get(request).count())
