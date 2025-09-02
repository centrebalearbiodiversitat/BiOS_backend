from django.db import models
from django.contrib.gis import forms as gis_forms


class LoweCaseCharField(models.CharField):
	def get_prep_value(self, value):
		value = super().get_prep_value(value)
		return value.lower() if value else value


class SRIDPolygonField(gis_forms.PolygonField):

	def validate(self, value):
		super().validate(value)

	def clean(self, value):
		if not value:
			return None

		if isinstance(value, str):
			value = value.strip()
			if not value.upper().startswith("SRID="):
				value = f"SRID={self.srid};{value}"

		geom = super().clean(value)

		return geom
