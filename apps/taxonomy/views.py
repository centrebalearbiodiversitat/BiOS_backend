from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .forms import TaxonomicLevelForms
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.taxonomy.models import TaxonomicLevel
from apps.taxonomy.serializers import TaxonomicLevelSerializer


class TaxonSearch(APIView):
    @swagger_auto_schema(
        operation_description="Search for a taxon by name.",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="Name of the taxon to search for.",
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('exact', openapi.IN_QUERY,
                              description="Indicates whether to search for an exact match. Defaults to False.", type=openapi.TYPE_BOOLEAN),
        ],
        responses={
            200: 'Success',
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

        results = TaxonomicLevel.objects.filter(**filters)

        return Response(
            TaxonomicLevelSerializer(
                results,
                many=True
            ).data
        )


class TaxonList(ListAPIView):

    serializer_class = TaxonomicLevelSerializer

    @swagger_auto_schema(
        operation_description="Get a list of taxa, with optional filtering.",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY,
                              description="Name of the taxon to search for.", type=openapi.TYPE_STRING),
            openapi.Parameter('rank', openapi.IN_QUERY,
                              description="Rank of the taxon to search for.", type=openapi.TYPE_STRING),
            openapi.Parameter('authorship', openapi.IN_QUERY,
                              description="Authorship of the taxon to search for.", type=openapi.TYPE_STRING),
            openapi.Parameter('parent', openapi.IN_QUERY,
                              description="Parent id of the taxon to search for.", type=openapi.TYPE_STRING),
            openapi.Parameter('exact', openapi.IN_QUERY,
                              description="Indicates whether to search for an exact match. Defaults to False.", type=openapi.TYPE_BOOLEAN),
        ],
        responses={
            200: 'Success',
            400: 'Bad Request',
        },
    )
    def filter_queryset(self, queryset):
        taxon_form = TaxonomicLevelForms(self.request.GET)

        if not taxon_form.is_valid():
            return Response(taxon_form.errors, status=400)

        exact = taxon_form.cleaned_data.get('exact', False)

        char_fields = ['name', 'rank', 'authorship']
        fk_fields = ['parent']

        for param in char_fields:
            value = self.request.query_params.get(param)

            if value:
                param = f'{param}__iexact' if exact else f'{param}__icontains'
                queryset = queryset.filter(**{param: value})

        for param in fk_fields:
            value = self.request.query_params.get(param)

            if value:
                queryset = queryset.filter(**{param: value})

        return queryset

    def get_queryset(self):
        queryset = TaxonomicLevel.objects.all()
        return self.filter_queryset(queryset)


class TaxonCRUD(APIView):
    def get(self, request, id):
        taxon = TaxonomicLevelSerializer(
            TaxonomicLevel.objects.filter(id=id).first()
        )

        return Response(taxon.data)


class TaxonParent(APIView):
    def get(self, request, id):
        taxon = TaxonomicLevelSerializer(
            TaxonomicLevel.objects.filter(id=id).first().parent
        )

        return Response(taxon.data)


class TaxonChildren(APIView):
    def get(self, request, id):
        taxon = TaxonomicLevelSerializer(
            TaxonomicLevel.objects.filter(id=id).first().children,
            many=True
        )

        return Response(taxon.data)
