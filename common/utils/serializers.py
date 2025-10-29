from django.core.paginator import Paginator
from rest_framework import serializers
from humps import camelize, decamelize

from common.utils.forms import PaginatorFieldForm


class BaseSerializer(serializers.ModelSerializer):
	class Meta:
		exclude = ("batch",)
		abstract = True


class CaseModelSerializer(BaseSerializer):
	"""
	A base serializer class for Django REST framework that automatically converts field names
	between camel case and snake case for responses and requests respectively.
	"""

	def to_representation(self, instance):
		data = super().to_representation(instance)
		data = camelize(data)
		return data

	def to_internal_value(self, data):
		data = decamelize(data)
		return super().to_internal_value(data)


def get_paginated_response(request, queryset, serializer_class, page_size=15):
	"""
	Generalized function to paginate and serialize a queryset.

	:param request: The HTTP request object
	:param queryset: The queryset to be paginated
	:param serializer_class: The serializer class to use
	:param page_size: Number of items per page (default: 15)
	:return: Response object with paginated data
	"""
	paginator = Paginator(queryset, page_size)
	page = PaginatorFieldForm.get_page(request.GET)
	try:
		items = paginator.page(page)
	except:
		items = []
	serialized_data = serializer_class(items, many=True).data

	return {"total": paginator.count, "pages": paginator.num_pages, "data": serialized_data}
