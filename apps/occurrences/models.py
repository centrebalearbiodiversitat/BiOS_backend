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
	MATERIAL_ENTITY = 6
	MATERIAL_SAMPLE = 7
	EVENT = 8
	TAXON = 9
	OCCURRENCE = 10

	BASIS_OF_RECORD = (
		(LIVING, "Living specimen"),
		(PRESERVED, "Preserved specimen"),
		(FOSSIL, "Fossil specimen"),
		(CITATION, "Material citation"),
		(HUMAN_OBSERVATION, "Human observation"),
		(MACHINE_OBSERVATION, "Machine observation"),
		(MATERIAL_ENTITY, "Material entity"),
		(MATERIAL_SAMPLE, "Material sample"),
		(EVENT, "Event"),
		(TAXON, "Taxon"),
		(OCCURRENCE, "Occurrence"),
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
		MATERIAL_ENTITY: "material_entity",
		"material_entity": MATERIAL_ENTITY,
		MATERIAL_SAMPLE: "material_sample",
		"material_sample": MATERIAL_SAMPLE,
		EVENT: "event",
		"event": EVENT,
		TAXON: "taxon",
		"taxon": TAXON,
		OCCURRENCE: "occurrence",
		"occurrence": OCCURRENCE,
	}

	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	voucher = models.CharField(max_length=255, null=True, blank=True)
	recorded_by = models.CharField(max_length=512, null=True, blank=True)
	collection_date_year = models.PositiveSmallIntegerField(null=True, blank=True)
	collection_date_month = models.PositiveSmallIntegerField(null=True, blank=True)
	collection_date_day = models.PositiveSmallIntegerField(null=True, blank=True)
	basis_of_record = models.PositiveSmallIntegerField(choices=BASIS_OF_RECORD)
	in_geography_scope = models.BooleanField()

	def clean(self):
		super().clean()
		if any([self.collection_date_year, self.collection_date_month, self.collection_date_day]):
			# If any of year, month, or day is missing, raise an error
			if not all([self.collection_date_year, self.collection_date_month, self.collection_date_day]):
				raise ValidationError("If specifying collection date, you must provide year, month, and day.")

			# Check if the year, month, and day form a valid date
			try:
				datetime.date(self.collection_date_year, self.collection_date_month, self.collection_date_day)
			except ValueError:
				raise ValidationError("The collection date you entered is not valid.")

	def __str__(self):
		return f"{self.taxonomy} ({self.voucher})"

	class Meta:
		indexes = [
			models.Index(fields=["taxonomy"]),
			models.Index(fields=["in_geography_scope"]),
			models.Index(fields=["taxonomy", "in_geography_scope"]),
			models.Index(fields=["location"]),
		]
