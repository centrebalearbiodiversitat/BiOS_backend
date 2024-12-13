from rest_framework import serializers
from humps import camelize, decamelize


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
