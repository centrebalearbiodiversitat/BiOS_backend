from apps.taxonomy.models import TaxonomicLevel
from apps.taxonomy.serializers import TaxonomicLevelSerializer, ParentSerializer, ChildrenSerializer
from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .forms import TaxonomicLevelForms




class TaxonSearch(APIView):

	@swagger_auto_schema(
		operation_description="Search for a taxon by name.",
		manual_parameters=[
			openapi.Parameter(
				'name',
				openapi.IN_QUERY,
				description="Name of the taxon to search for.",
				type=openapi.TYPE_STRING,
				required=True
			),
			openapi.Parameter(
				'exact',
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN
			),
		],
		responses={
			200: 'Success',
			204: 'No Content',
			400: 'Bad Request',
		},
	)

	def get(self, request):
		taxon_form = TaxonomicLevelForms(request.GET)

		filters = {}

		if not taxon_form.is_valid():
			return Response(taxon_form.errors, status=400)

		query = taxon_form.cleaned_data.get('name')
		exact = taxon_form.cleaned_data.get('exact', False)

		filters['name__iexact' if exact else 'name__icontains'] = query

		queryset = TaxonomicLevel.objects.filter(**filters)

		return Response(TaxonomicLevelSerializer(queryset, many=True).data)


class TaxonList(ListAPIView):
	serializer_class = TaxonomicLevelSerializer

	@swagger_auto_schema(
		operation_description="Get a list of taxa, with optional filtering.",
		manual_parameters=[
			openapi.Parameter(
				'name',
				openapi.IN_QUERY,
				description="Name of the taxon to search for.",
				type=openapi.TYPE_STRING
			),
			openapi.Parameter(
				'rank',
				openapi.IN_QUERY,
				description="Rank id of the taxon to search for.",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				'scientificNameAuthorship',
				openapi.IN_QUERY,
				description="Authorship id of the taxon to search for.",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				'parent',
				openapi.IN_QUERY,
				description="Parent id of the taxon to search for.",
				type=openapi.TYPE_INTEGER
			),
			openapi.Parameter(
				'exact',
				openapi.IN_QUERY,
				description="Indicates whether to search for an exact match. Defaults to False.",
				type=openapi.TYPE_BOOLEAN
			),
		],
		responses={
			200: 'Success',
			204: 'No Content',
			400: 'Bad Request',
		},
	)

	def get(self, request):
		taxon_form = TaxonomicLevelForms(self.request.GET)

		if not taxon_form.is_valid():
			return Response(taxon_form.errors, status=400)

		exact = taxon_form.cleaned_data.get('exact', False)

		str_fields = ['name']
		num_fields = ['authorship', 'parent', 'rank']

		filters = {}

		for param in str_fields:
			value = request.query_params.get(param)

			if value:
				param = f'{param}__iexact' if exact else f'{param}__icontains'
				filters[param] = value

		for param in num_fields:
			value = request.query_params.get(param)

			if value:
				filters[param] = value

		queryset = TaxonomicLevel.objects.filter(**filters)

		return Response(TaxonomicLevelSerializer(queryset, many=True).data)


class TaxonCRUD(APIView):

	@swagger_auto_schema(
		operation_description="Retrieve a specific TaxonomicLevel instance by its id",
		manual_parameters=[
			openapi.Parameter(
				'id',
				openapi.IN_QUERY,
				description="ID of the taxon to retrieve",
				type=openapi.TYPE_INTEGER,
				required=True
			)
		],
		responses={
			200: 'Success',
			204: 'No Content',
			400: 'Bad Request'
		}
	)

	def get(self, request):
		taxon_form = TaxonomicLevelForms(self.request.GET)

		if not taxon_form.is_valid():
			raise ValidationError(taxon_form.errors)

		id = request.query_params.get('id')
		queryset = TaxonomicLevel.objects.filter(id=id).first()

		return Response(TaxonomicLevelSerializer(queryset).data)


class TaxonParent(APIView):

	@swagger_auto_schema(
		operation_description="Get the parent of the taxon given its ID",
		manual_parameters=[
			openapi.Parameter(
				name='id',
				in_=openapi.IN_QUERY,
				description='ID of the taxon',
				type=openapi.TYPE_INTEGER,
				required=True
			),
		],
		responses={
			200: 'Success',
			204: 'No Content',
			400: "Bad Request"
		},
	)
	
	def get(self, request):
		taxon_form = TaxonomicLevelForms(self.request.GET)

		if not taxon_form.is_valid():
			raise ValidationError(taxon_form.errors)

		id = request.query_params.get('id')
		queryset = TaxonomicLevel.objects.filter(id=id).first().parent

		return Response(ParentSerializer(queryset).data)


class TaxonChildren(APIView):

	@swagger_auto_schema(
		operation_description="Get taxonomic level children",
		manual_parameters=[
			openapi.Parameter(
				name="id",
				in_=openapi.IN_QUERY,
				type=openapi.TYPE_INTEGER,
				description="ID of the taxonomic level",
				required=True
			)
		],
		responses={
			200: "Success",
			204: 'No Content',
			400: "Bad Request"
		}
	)
	
	def get(self, request):
		taxon_form = TaxonomicLevelForms(self.request.GET)

		if not taxon_form.is_valid():
			raise ValidationError(taxon_form.errors)

		id = request.query_params.get('id')
		queryset = TaxonomicLevel.objects.filter(id=id).first()
		queryset = queryset.children.all()
		return Response(ChildrenSerializer(queryset, many = True).data)