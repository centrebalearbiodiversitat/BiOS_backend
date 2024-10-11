import datetime

from django.core.exceptions import ValidationError
from django.db import models
from apps.taxonomy.models import TaxonomicLevel
from common.utils.models import LatLonModel, ReferencedModel


class Occurrence(ReferencedModel, LatLonModel):
	LIVING = 0
	PRESERVED = 1
	FOSSIL = 2
	CITATION = 3
	HUMAN_OBSERVATION = 4
	MACHINE_OBSERVATION = 5
	UNKNOWN = 6
	INVALID = 7

	BASIS_OF_RECORD = (
		(LIVING, "Living specimen"),
		(PRESERVED, "Preserved specimen"),
		(FOSSIL, "Fossil specimen"),
		(CITATION, "Material citation"),
		(HUMAN_OBSERVATION, "Human observation"),
		(MACHINE_OBSERVATION, "Machine observation"),
		(UNKNOWN, "Unknown"),
		(INVALID, "Invalid"),
	)

	TRANSLATE_BASIS_OF_RECORD = {
		LIVING: "living_specimen",
		"living_specimen": LIVING,
		PRESERVED: "preserved_specimen",
		"preserved_specimen": PRESERVED,
		FOSSIL: "fossil_specimen",
		"fossil_specimen": FOSSIL,
		CITATION: "material_citation",
		"material_citation": CITATION,
		HUMAN_OBSERVATION: "human_observation",
		"human_observation": HUMAN_OBSERVATION,
		MACHINE_OBSERVATION: "machine_observation",
		"machine_observation": MACHINE_OBSERVATION,
		UNKNOWN: "unknown",
		"unknown": UNKNOWN,
		INVALID: "invalid",
		"invalid": INVALID,
	}

	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	voucher = models.CharField(max_length=255, null=True, blank=True)
	recorded_by = models.CharField(max_length=512, null=True, blank=True)
	collection_date_year = models.PositiveSmallIntegerField(null=True, blank=True)
	collection_date_month = models.PositiveSmallIntegerField(null=True, blank=True)
	collection_date_day = models.PositiveSmallIntegerField(null=True, blank=True)
	basis_of_record = models.PositiveSmallIntegerField(choices=BASIS_OF_RECORD)
	in_cbb_scope = models.BooleanField()

	def clean(self):
		super().clean()
		if any([self.collection_date_year, self.collection_date_month, self.collection_date_day]):
			# If any of year, month, or day is missing, raise an error
			if not all([self.collection_date_year, self.collection_date_month, self.collection_date_day]):
				raise ValidationError('If specifying collection date, you must provide year, month, and day.')

			# Check if the year, month, and day form a valid date
			try:
				datetime.date(
					self.collection_date_year,
					self.collection_date_month,
					self.collection_date_day
				)
			except ValueError:
				raise ValidationError('The collection date you entered is not valid.')

	def __str__(self):
		return f"{self.taxonomy} ({self.voucher})"

	class Meta:
		indexes = [
			models.Index(fields=['in_cbb_scope']),
		]
