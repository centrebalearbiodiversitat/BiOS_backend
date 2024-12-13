from apps.tags.serializers import SystemSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.API.exceptions import CBBAPIException
from apps.tags.models import Directive, Habitat, IUCNData, System, TaxonomicLevel, TaxonTag
from apps.tags.serializers import (
	HabitatSerializer,
	IUCNDataSerializer,
	TaxonTagSerializer,
	DirectiveSerializer
)

from .forms import (
	DirectiveForm,
	IUCNDataForm,
	SystemForm,
	TaxonTagForm
)


# class TagListView(APIView):
# 	@swagger_auto_schema(
# 		tags=["Tag"],
# 		operation_description="Retrieve a specific tag instance by its id",
# 		manual_parameters=[
# 			openapi.Parameter(
# 				"id",
# 				openapi.IN_QUERY,
# 				description="ID of the tag to retrieve",
# 				type=openapi.TYPE_INTEGER,
# 				required=True,
# 			)
# 		],
# 		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
# 	)
# 	def get(self, request):
# 		tag_form = TagForm(self.request.GET)

# 		if not tag_form.is_valid():
# 			raise CBBAPIException(tag_form.errors, code=400)

# 		tag_id = tag_form.cleaned_data.get("id")
# 		if not tag_id:
# 			raise CBBAPIException("Missing id parameter", code=400)

# 		try:
# 			tag = Tag.objects.get(id=tag_id)
# 		except Tag.DoesNotExist:
# 			raise CBBAPIException("Tag does not exist", code=404)

# 		return Response(TagSerializer(tag).data)


class TaxonTagListView(APIView):
	@swagger_auto_schema(
		tags=["Tags"],
		operation_description="Retrieve a specific taxonomic tags instance by its taxonomic level id",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="ID of the taxon data to retrieve",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = TaxonTagForm(self.request.GET)

		if not taxon_form.is_valid():
			raise CBBAPIException(taxon_form.errors, code=400)

		taxon_id = taxon_form.cleaned_data.get("taxonomy")

		if not taxon_id:
			raise CBBAPIException("Missing taxonomy id parameter", code=400)

		try:
			taxon = TaxonTag.objects.get(taxonomy=taxon_id)
		except TaxonTag.DoesNotExist:
			raise CBBAPIException("Taxonomic tags does not exist", code=404)

		return Response(TaxonTagSerializer(taxon).data)


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
	@swagger_auto_schema(
		tags=["Tags"],
		operation_description="Obtains the habitats in which a taxonomic level is found by its ID.",
		manual_parameters=[
			openapi.Parameter(
				name="taxonomy",
				in_=openapi.IN_QUERY,
				description="ID of the taxon to retrieve it's habitats",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		taxon_form = IUCNDataForm(data=request.GET)

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

		iucn_data = IUCNData.objects.filter(taxonomy__in=descendants)

		habitats = Habitat.objects.filter(iucndata__in=iucn_data).distinct()

		return Response(HabitatSerializer(habitats, many=True).data)


class IUCNDataListView(APIView):
	@swagger_auto_schema(
		tags=["Tags"],
		operation_description="Retrieve the conservation status and habitats of a taxonomic level by its ID",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="ID of the taxonomic level",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		iucn_form = IUCNDataForm(self.request.GET)

		if not iucn_form.is_valid():
			raise CBBAPIException(iucn_form.errors, code=400)

		taxon_id = iucn_form.cleaned_data.get("taxonomy")

		if not taxon_id:
			raise CBBAPIException("Missing taxonomy id parameter", code=400)
		try:
			taxon = IUCNData.objects.get(taxonomy=taxon_id)
		except IUCNData.DoesNotExist:
			raise CBBAPIException("Conservation status does not exist", code=404)

		return Response(IUCNDataSerializer(taxon).data)

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
	@swagger_auto_schema(
		tags=["Tags"],
		operation_description="Obtains the habitats in which a taxonomic level is found by its ID.",
		manual_parameters=[
			openapi.Parameter(
				name="taxonomy",
				in_=openapi.IN_QUERY,
				description="ID of the taxon to retrieve it's habitats",
				type=openapi.TYPE_INTEGER,
				required=True,
			),
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		system_form = SystemForm(data=request.GET)

		if not system_form.is_valid():
			raise CBBAPIException(system_form.errors, 400)

		taxonomy = system_form.cleaned_data.get("taxonomy", None)

		if not taxonomy:
			raise CBBAPIException("Missing taxonomy id parameter", 400)

		try:
			taxon_parent = TaxonomicLevel.objects.get(id=taxonomy)
		except TaxonomicLevel.DoesNotExist:
			raise CBBAPIException("Taxonomic level does not exist", 404)

		descendants = taxon_parent.get_descendants(include_self=True)

		system = System.objects.filter(taxonomy__in=descendants)


		return Response(SystemSerializer(system, many=True).data)


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
	@swagger_auto_schema(
		tags=["Tags"],
		operation_description="Retrieve a specific directive instance by its taxonomic level id",
		manual_parameters=[
			openapi.Parameter(
				"taxonomy",
				openapi.IN_QUERY,
				description="ID of the taxonomic level to retrieve",
				type=openapi.TYPE_INTEGER,
				required=True,
			)
		],
		responses={200: "Success", 400: "Bad Request", 404: "Not Found"},
	)
	def get(self, request):
		directive_form = DirectiveForm(self.request.GET)

		if not directive_form.is_valid():
			raise CBBAPIException(directive_form.errors, code=400)

		taxon_id = directive_form.cleaned_data.get("taxonomy")

		if not taxon_id:
			raise CBBAPIException("Missing taxonomy id parameter", code=400)

		try:
			taxon = Directive.objects.get(taxonomy=taxon_id)
		except TaxonTag.DoesNotExist:
			raise CBBAPIException("Taxonomic tags does not exist", code=404)

		return Response(DirectiveSerializer(taxon).data)
