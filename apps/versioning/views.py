from django.core.exceptions import ValidationError
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from common.utils.models import SynonymModel
from common.utils.serializers import CaseModelSerializer
from .models import Source, Batch, OriginSource
from .serializers import SourceSerializer, OriginSourceSerializer
from .forms import SourceForm, OriginSourceForm


class SourceView(APIView):
	@swagger_auto_schema(
        operation_description="Retrieve a Source by name",
		manual_parameters=[
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the source to search for.",
				type=openapi.TYPE_STRING,
				required=True,
			),
			openapi.Parameter(
				"exact",
				openapi.IN_QUERY,
				description="Whether to search for an exact match or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
			)
		],
		responses={
            200: 'Success',
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
	def get(self, request):
		source_form = SourceForm(self.request.GET)

		if not source_form.is_valid():
			raise ValidationError(source_form.errors)	

		filters = {}

		query = source_form.cleaned_data.get("name")
		exact = source_form.cleaned_data.get("exact", False)

		filters["name__iexact" if exact else "name__icontains"] = query

		try:
			source = Source.objects.get(**filters)
		except Source.DoesNotExist:
			raise Http404

		return Response((
			SourceSerializer(
				source,
				many=False)
		).data)


class SourceList(APIView):
	@swagger_auto_schema(
        operation_description="List Sources with optional filters",
        manual_parameters = [
			openapi.Parameter(
				"name",
				openapi.IN_QUERY,
				description="Name of the source to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			),
			openapi.Parameter(
				"accepted",
				openapi.IN_QUERY,
				description="Whether to search for accepted or not.",
				type=openapi.TYPE_BOOLEAN,
				required=False,
				default=False,
			),
			openapi.Parameter(
				"origin",
				openapi.IN_QUERY,
				description="Origin of the source to search for.",
				type=openapi.TYPE_STRING,
				required=False,
			)			
		],
        responses={
            200: "Success",
            400: "Bad Request",
			404: "Not Found"
        }
    )
	def get(self, request):
		source_form = SourceForm(data = self.request.GET)
		if not source_form.is_valid():
			return Response(source_form.errors, status=400)

		filters = {}
		for param in source_form.cleaned_data:
			value = source_form.cleaned_data.get(param)
			if value or isinstance(value, int):
				filters[param] = value
		if filters:
			queryset = Source.objects.filter(**filters)

		else:
			queryset = Source.objects.none()

		return Response((
			SourceSerializer(
				queryset,
				many=True)
		).data)

# # TERMINAR DE REVISAR EL FILTRADO POR DATETIME
# class BatchView(APIView):
# 	def get(self, request):
# 		batch_form = BatchForm(data = self.request.GET)

# 		if not batch_form.is_valid():
# 			raise ValidationError(batch_form.errors)

# 		filters = {}
# 		for param in batch_form.cleaned_data:
# 			value = batch_form.cleaned_data.get(param)
# 			if value or isinstance(value, int):
# 				filters[param] = value
# 		if filters:
# 			try:
# 				print("ENTRA")
# 				print(filters)
# 				queryset = Batch.objects.filter(**filters)
# 			except Batch.DoesNotExist:
# 				raise Http404

# 			return Response((
# 				BatchSerializer(
# 					queryset,
# 					many=False)
# 			).data)

class OriginSourceView(APIView):
	@swagger_auto_schema(
        operation_description="List origin sources with optional filters",
        manual_parameters=[
			openapi.Parameter(
				"origin_id",
				openapi.IN_QUERY,
				description="Origin id of the origin source to search for.",
				type=openapi.TYPE_INTEGER,
				required=False,
			),
			openapi.Parameter(
				"source",
				openapi.IN_QUERY,
				description="Source of the origin source to search for",
				type=openapi.TYPE_INTEGER,
				required=False,
			)
		],
        responses={
            200: 'Success',
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
	def get(self, request):
		origin_source_form = OriginSourceForm(data = self.request.GET)

		if not origin_source_form.is_valid():
			raise ValidationError(origin_source_form.errors)

		filters = {}
		for param in origin_source_form.cleaned_data:
			value = origin_source_form.cleaned_data.get(param)
			if value or isinstance(value, int):
				filters[param] = value
		if filters:
			try:
				queryset = OriginSource.objects.filter(**filters)
			except OriginSource.DoesNotExist:
				raise Http404
		else:
			queryset = OriginSource.objects.all()

		return Response((
			OriginSourceSerializer(
				queryset,
				many=True)
		).data)

# class SynonymModelView(APIView):
# 	def get(self, request):
# 		synonym_form = SynonymModelForm(self.request.GET)

# 		if not synonym_form.is_valid():
# 			raise ValidationError(synonym_form.errors)
		
# 		name = synonym_form.cleaned_data.get('name')
# 		try:
# 			synonym_models = SynonymModel.objects.get(name=name)
# 			print("200")
# 		except SynonymModel.DoesNotExist:
# 			print("404")
# 			raise Http404

# 		serializer = SynonymModelSerializer(synonym_models, many=False)
# 		return Response(serializer.data)