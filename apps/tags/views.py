from apps.tags.serializers import SystemSerializer
from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.API.exceptions import CBBAPIException
from apps.tags.models import Directive, Habitat, IUCNData, System, TaxonomicLevel, TaxonTag
from apps.tags.serializers import HabitatSerializer, IUCNDataSerializer, TaxonTagSerializer, DirectiveSerializer
from common.utils.forms import TaxonomyForm

from common.utils.custom_swag_schema import custom_swag_schema


m1 = [
	openapi.Parameter(
		"taxonomy",
		openapi.IN_QUERY,
		description="Taxon ID",
		type=openapi.TYPE_INTEGER,
		required=True
	)
]

class TaxonTagListView(APIView):
	@custom_swag_schema(
		tags="Tags",
		operation_id="Get the tags by taxon ID",
		operation_description="Retrieve the tags by taxon ID.",
		manual_parameters=m1
	)
	def get(self, request):
		taxon_form = TaxonomyForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("taxonomy")
		if not taxon_id:
			raise CBBAPIException("Missing taxonomy id parameter", code=400)

		taxon_tags = TaxonTag.objects.filter(taxonomy=taxon_id)

		return Response(TaxonTagSerializer(taxon_tags, many=True).data)


# class TaxonTagFilter:
# 	def get(self, request):
# 		taxon_data_form = TaxonTagForm(data=request.GET)

# 		if not taxon_data_form.is_valid():
# 			raise CBBAPIException(taxon_data_form.errors, code=400)

# 		taxonomy = taxon_data_form.cleaned_data.get("taxonomy", None)
# 		if not taxonomy:
# 			raise CBBAPIException("Missing taxonomy id parameter", 400)

# 		exact = taxon_data_form.cleaned_data.get("exact", False)
# 		str_fields = ["habitat"]

# 		filters = {}
# 		for param in taxon_data_form.cleaned_data:
# 			if param != "exact":
# 				if param in str_fields:
# 					value = taxon_data_form.cleaned_data.get(param)

# 					if value:
# 						param = f"{param}__iexact" if exact else f"{param}__icontains"
# 						filters[param] = value
# 				else:
# 					value = taxon_data_form.cleaned_data.get(param)
# 					if value or isinstance(value, int):
# 						filters[param] = value

# 		if filters:
# 			query = TaxonTag.objects.filter(**filters)
# 		else:
# 			query = TaxonTag.objects.none()

# 		return query


# class TaxonTagListView(TaxonTagFilter, ListAPIView):
# 	@swagger_auto_schema(
# 		tags=["Taxon Data"],
# 		operation_description="Get a list of taxon data with filtering.",
# 		manual_parameters=[
# 			openapi.Parameter("taxonomy", openapi.IN_QUERY, description="ID of the taxon", type=openapi.TYPE_INTEGER),
# 			openapi.Parameter(
# 				"iucn_global",
# 				openapi.IN_QUERY,
# 				description="IUCN Global status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter(
# 				"iucn_europe",
# 				openapi.IN_QUERY,
# 				description="IUCN Europe status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter(
# 				"iucn_mediterranean",
# 				openapi.IN_QUERY,
# 				description="IUCN Mediterranean status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter("invasive", openapi.IN_QUERY, description="Is invasive?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("domesticated", openapi.IN_QUERY, description="Is domesticated?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("freshwater", openapi.IN_QUERY, description="Inhabit freshwater?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("marine", openapi.IN_QUERY, description="Inhabit marine?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("terrestrial", openapi.IN_QUERY, description="Inhabit terrestrial?", type=openapi.TYPE_BOOLEAN),
# 		],
# 		responses={200: "Success", 400: "Bad Request"},
# 	)
# 	def get(self, request):
# 		return Response(TaxonTagSerializer(super().get(request), many=True).data)


# class TaxonTagCountView(TaxonTagFilter, ListAPIView):
# 	@swagger_auto_schema(
# 		tags=["Taxon Data"],
# 		operation_description="Get a list of taxon data with filtering.",
# 		manual_parameters=[
# 			openapi.Parameter("taxonomy_id", openapi.IN_QUERY, description="ID of the taxon", type=openapi.TYPE_INTEGER),
# 			openapi.Parameter(
# 				"iucn_global",
# 				openapi.IN_QUERY,
# 				description="IUCN Global status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter(
# 				"iucn_europe",
# 				openapi.IN_QUERY,
# 				description="IUCN Europe status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter(
# 				"iucn_mediterranean",
# 				openapi.IN_QUERY,
# 				description="IUCN Mediterranean status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter("invasive", openapi.IN_QUERY, description="Is invasive?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("domesticated", openapi.IN_QUERY, description="Is domesticated?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("freshwater", openapi.IN_QUERY, description="Inhabit freshwater?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("marine", openapi.IN_QUERY, description="Inhabit marine?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("terrestrial", openapi.IN_QUERY, description="Inhabit terrestrial?", type=openapi.TYPE_BOOLEAN),
# 		],
# 		responses={200: "Success", 400: "Bad Request"},
# 	)
# 	def get(self, request):
# 		return Response(super().get(request).count())


# class TaxonTagInvasiveView(APIView):

# 	def get(self, request):
# 		taxon_form = TaxonTagForm(data=request.GET)

# 		if not taxon_form.is_valid():
# 			raise CBBAPIException(taxon_form.errors, 400)

# 		tag = taxon_form.cleaned_data.get("tag", None)

# 		if not tag:
# 			raise CBBAPIException("Missing tag parameter", 400)

# 		invasive_species = TaxonTag.objects.filter(
# 			tags__name__iexact=tag
# 		).prefetch_related(
# 			Prefetch('taxonomy',queryset=TaxonomicLevel.objects.all()),"tags"
# 		).values_list("taxonomy", flat=True)

# 		invasive_species = list(TaxonomicLevel.objects.filter(pk__in=invasive_species))

# 		return Response(BaseTaxonomicLevelSerializer(invasive_species, many=True).data)


class HabitatsListView(APIView):
	@custom_swag_schema(
		tags="Tags",
		operation_id="Get habitats by taxon ID",
		operation_description="Obtains the habitats in which a taxon is found by its ID.",
		manual_parameters=m1,
	)
	def get(self, request):
		taxon_form = TaxonomyForm(data=request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, 400)

		taxonomy = taxon_form.cleaned_data.get("taxonomy", None)
		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)

		try:
			taxon_parent = TaxonomicLevel.objects.get(id=taxonomy)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		descendants = taxon_parent.get_descendants(include_self=True)

		filtered_habitats_queryset = Habitat.objects.filter(habitattaxonomy__taxonomy_id__in=descendants).distinct()

		return Response(HabitatSerializer(filtered_habitats_queryset, many=True).data)


class IUCNDataListView(APIView):
	@custom_swag_schema(
		tags="Tags",
		operation_id="Get IUCN data by taxon ID",
		operation_description="Retrieve the conservation status of a taxon by its ID.",
		manual_parameters=m1
	)
	def get(self, request):
		iucn_form = TaxonomyForm(self.request.GET)

		if not iucn_form.is_valid():
			raise CBBAPIException(iucn_form.errors, code=400)

		taxon_id = iucn_form.cleaned_data.get("taxonomy")
		if not taxon_id:
			raise CBBAPIException("Missing taxonomy id parameter", code=400)
		try:
			taxon = TaxonomicLevel.objects.get(id=taxon_id)

		except IUCNData.DoesNotExist:
			raise CBBAPIException("Conservation status does not exist", code=404)

		filtered_iucn_queryset = IUCNData.objects.filter(taxonomy_id__in=[taxon]).distinct()

		return Response(IUCNDataSerializer(filtered_iucn_queryset, many=True).data)

# class IUCNDataFilter:
# 	def get(self, request):
# 		taxon_data_form = IUCNDataForm(data=request.GET)

# 		if not taxon_data_form.is_valid():
# 			raise CBBAPIException(taxon_data_form.errors, code=400)

# 		taxonomy = taxon_data_form.cleaned_data.get("taxonomy", None)
# 		if not taxonomy:
# 			raise CBBAPIException("Missing taxonomy id parameter", 400)

# 		exact = taxon_data_form.cleaned_data.get("exact", False)
# 		str_fields = ["habitat"]

# 		filters = {}
# 		for param in taxon_data_form.cleaned_data:
# 			if param != "exact":
# 				if param in str_fields:
# 					value = taxon_data_form.cleaned_data.get(param)

# 					if value:
# 						param = f"{param}__iexact" if exact else f"{param}__icontains"
# 						filters[param] = value
# 				else:
# 					value = taxon_data_form.cleaned_data.get(param)
# 					if value or isinstance(value, int):
# 						filters[param] = value

# 		if filters:
# 			query = IUCNData.objects.filter(**filters)
# 		else:
# 			query = IUCNData.objects.none()

# 		return query


# class IUCNDataListView(IUCNDataFilter, ListAPIView):
# 	@swagger_auto_schema(
# 		tags=["Taxon Data"],
# 		operation_description="Get a list of taxon data with filtering.",
# 		manual_parameters=[
# 			openapi.Parameter("taxonomy", openapi.IN_QUERY, description="ID of the taxon", type=openapi.TYPE_INTEGER),
# 			openapi.Parameter(
# 				"iucn_global",
# 				openapi.IN_QUERY,
# 				description="IUCN Global status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter(
# 				"iucn_europe",
# 				openapi.IN_QUERY,
# 				description="IUCN Europe status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter(
# 				"iucn_mediterranean",
# 				openapi.IN_QUERY,
# 				description="IUCN Mediterranean status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter("invasive", openapi.IN_QUERY, description="Is invasive?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("domesticated", openapi.IN_QUERY, description="Is domesticated?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("freshwater", openapi.IN_QUERY, description="Inhabit freshwater?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("marine", openapi.IN_QUERY, description="Inhabit marine?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("terrestrial", openapi.IN_QUERY, description="Inhabit terrestrial?", type=openapi.TYPE_BOOLEAN),
# 		],
# 		responses={200: "Success", 400: "Bad Request"},
# 	)
# 	def get(self, request):
# 		return Response(IUCNDataSerializer(super().get(request), many=True).data)


# class IUCNDataCountView(IUCNDataFilter, ListAPIView):
# 	@swagger_auto_schema(
# 		tags=["Taxon Data"],
# 		operation_description="Get a list of taxon data with filtering.",
# 		manual_parameters=[
# 			openapi.Parameter("taxonomy_id", openapi.IN_QUERY, description="ID of the taxon", type=openapi.TYPE_INTEGER),
# 			openapi.Parameter(
# 				"iucn_global",
# 				openapi.IN_QUERY,
# 				description="IUCN Global status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter(
# 				"iucn_europe",
# 				openapi.IN_QUERY,
# 				description="IUCN Europe status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter(
# 				"iucn_mediterranean",
# 				openapi.IN_QUERY,
# 				description="IUCN Mediterranean status",
# 				type=openapi.TYPE_STRING,
# 				enum=[str(c[0]) for c in IUCNData.CS_CHOICES],
# 			),
# 			openapi.Parameter("invasive", openapi.IN_QUERY, description="Is invasive?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("domesticated", openapi.IN_QUERY, description="Is domesticated?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("freshwater", openapi.IN_QUERY, description="Inhabit freshwater?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("marine", openapi.IN_QUERY, description="Inhabit marine?", type=openapi.TYPE_BOOLEAN),
# 			openapi.Parameter("terrestrial", openapi.IN_QUERY, description="Inhabit terrestrial?", type=openapi.TYPE_BOOLEAN),
# 		],
# 		responses={200: "Success", 400: "Bad Request"},
# 	)
# 	def get(self, request):
# 		return Response(super().get(request).count())


class SystemListView(APIView):
	@custom_swag_schema(
		tags="Tags",
		operation_id="Get system by taxon ID",
		operation_description="Obtains the system information of a taxon by its ID.",
		manual_parameters=m1
	)
	def get(self, request):
		system_form = TaxonomyForm(data=request.GET)

		if not system_form.is_valid():
			raise CBBAPIException(system_form.errors, 400)

		taxonomy = system_form.cleaned_data.get("taxonomy", None)
		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)

		# try:
		# 	taxon_parent = TaxonomicLevel.objects.get(id=taxonomy)
		# except TaxonomicLevel.DoesNotExist:
		# 	raise CBBAPIException("Taxonomic level does not exist", 404)

		# descendants = taxon_parent.get_descendants(include_self=True)

		try:
			system = System.objects.get(taxonomy=taxonomy)
		except System.DoesNotExist:
			system = None

		return Response(SystemSerializer(system).data)


# class SystemDetailView(APIView):
# 	@swagger_auto_schema(
# 		tags=["Taxon Data"],
# 		operation_description="Retrieve the systems in wich a taxonomic level is found by its ID",
# 		manual_parameters=[
# 			openapi.Parameter(
# 				"taxonomy",
# 				openapi.IN_QUERY,
# 				description="ID of the taxonomic level",
# 				type=openapi.TYPE_INTEGER,
# 				required=True,
# 			)
# 		],
# 		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
# 	)

# 	def get(self, request):

# 		system_form = IdFieldForm(self.request.GET)

# 		if not system_form.is_valid():
# 			raise CBBAPIException(system_form.errors, code=400)
# 		try:
# 			system = System.objects.get(id=system_form.cleaned_data.get("id"))
# 		except System.DoesNotExist:
# 			raise CBBAPIException("System does not exist.", code=404)

# 		serializer = SystemSerializer(system)
# 		return Response(serializer.data)


class DirectiveListView(APIView):
	@custom_swag_schema(
		tags="Tags",
		operation_id="Get directive by taxon ID",
		operation_description="Retrieve directives instance by taxon ID.",
		manual_parameters=m1
	)
	def get(self, request):
		directive_form = TaxonomyForm(self.request.GET)

		if not directive_form.is_valid():
			raise CBBAPIException(directive_form.errors, code=400)

		taxon_id = directive_form.cleaned_data.get("taxonomy")
		if not taxon_id:
			raise CBBAPIException("Missing taxonomy id parameter", code=400)

		try:
			directives = Directive.objects.get(taxonomy=taxon_id)
		except Directive.DoesNotExist:
			directives = None

		return Response(DirectiveSerializer(directives).data)
