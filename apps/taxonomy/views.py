import csv

from django.db.models import Q
from django.http import StreamingHttpResponse

from apps.taxonomy.models import TaxonomicLevel, Authorship
from apps.taxonomy.serializers import BaseTaxonomicLevelSerializer, AuthorshipSerializer
from apps.API.exceptions import CBBAPIException
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .forms import TaxonomicLevelForm, AuthorshipForm
from ..versioning.serializers import OriginSourceSerializer
from common.utils.utils import EchoWriter


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

		if not query:
			return Response(BaseTaxonomicLevelSerializer(TaxonomicLevel.objects.none(), many=True).data)

		queryset = TaxonomicLevel.objects
		for query in query.split(" "):
			filters["name__iexact" if exact else "name__icontains"] = query

			queryset = queryset.filter(**filters)

			if len(query) > 3:
				sub_genus = None
				for instance in queryset.filter(rank=TaxonomicLevel.GENUS):
					if sub_genus:
						sub_genus |= Q(tree_id=instance.tree_id, lft__gte=instance.lft, rght__lte=instance.rght)
					else:
						sub_genus = Q(tree_id=instance.tree_id, lft__gte=instance.lft, rght__lte=instance.rght)

				if sub_genus:
					queryset |= TaxonomicLevel.objects.filter(sub_genus)

		return Response(BaseTaxonomicLevelSerializer(queryset[:10], many=True).data)


class TaxonListView(ListAPIView):
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
		taxon_form = TaxonomicLevelForm(data=request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		exact = taxon_form.cleaned_data.get("exact", False)
		synonym = taxon_form.cleaned_data.get("synonym", False)
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
					if value or isinstance(value, int):
						filters[param] = value

		if synonym:
			filters["accepted"] = False

		if filters:
			query = TaxonomicLevel.objects.filter(**filters)
		else:
			query = TaxonomicLevel.objects.none()

		return Response(BaseTaxonomicLevelSerializer(query, many=True).data)


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


class TaxonChildrenView(APIView):
	@swagger_auto_schema(
		tags=["Taxonomy"],
		operation_description="Get the direct children of the taxon given its ID",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the taxonomic level",
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
			raise CBBAPIException("Taxonomic level does not exist.", code=404)

		return Response(BaseTaxonomicLevelSerializer(taxon.get_children(), many=True).data)


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
			raise CBBAPIException(taxon_form.errors, code=400)

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
	current_name = ''
	for rank in ranks:
		if current is None:
			break

		if current.rank in [TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY]:
			current_name = f'{current_name} {current.name}'
		else:
			current_name = current.name

		if rank == current.rank:
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

		try:
			head_taxon = TaxonomicLevel.objects.get(id=taxon_form.cleaned_data.get("id"))
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", code=404)

		ranks = [rank[1] for rank in TaxonomicLevel.RANK_CHOICES]
		ranks_map = [rank[0] for rank in TaxonomicLevel.RANK_CHOICES]
		to_csv = [[
			'id', 'status', 'taxonRank', *list(sum([(f'{rank.lower()}', f'authorship{rank}') for rank in ranks], ())),
		]]

		upper_taxon = head_taxon.get_ancestors(include_self=False)  #.exclude(name__iexact='Biota')
		upper_taxon = list(upper_taxon)
		# upper_taxon = map_taxa_to_rank(ranks_map, upper_taxon)
		# print(upper_taxon)
		checklist = head_taxon.get_descendants(include_self=True)
		current_taxon = []
		last_level = -1
		for taxon in checklist:
			if last_level >= taxon.level:
				current_taxon = current_taxon[:len(current_taxon) - (last_level - taxon.level + 1)]

			current_taxon.append(taxon)
			to_csv.append([taxon.id, taxon.readable_status(), taxon.readable_rank(), *map_taxa_to_rank(ranks_map, upper_taxon + current_taxon)])
			last_level = taxon.level

		csv_writer = csv.writer(EchoWriter())
		return StreamingHttpResponse(
			(csv_writer.writerow(row) for row in to_csv),
			content_type="text/csv",
			headers={"Content-Disposition": f'attachment; filename="{head_taxon}_checklist.csv"'}
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
		authorship_form = AuthorshipForm(self.request.GET)

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
