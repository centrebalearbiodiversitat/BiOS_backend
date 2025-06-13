from django.db import models
from apps.taxonomy.models import TaxonomicLevel
from common.utils.models import ReferencedModel


class System(ReferencedModel):
	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	freshwater = models.BooleanField(default=None, null=True)
	marine = models.BooleanField(default=None, null=True)
	terrestrial = models.BooleanField(default=None, null=True)

	class Meta:
		unique_together = ["taxonomy"]

	def __str__(self):
		return f"{self.taxonomy} - freshwater: {self.freshwater}, marine: {self.marine}, terrestrial: {self.terrestrial}"


class Tag(models.Model):
	DOE = 0

	TAG_TYPE_CHOICES = ((DOE, "degreeOfEstablishment"),)

	TRANSLATE_TYPE = {
		"degreeOfEstablishment": DOE,
		DOE: "degreeOfEstablishment",
	}

	name = models.CharField(max_length=255)
	tag_type = models.PositiveSmallIntegerField(choices=TAG_TYPE_CHOICES)

	def translate_tag_type(self):
		return Tag.TRANSLATE_TYPE[self.tag_type]

	def __str__(self):
		return f"({self.translate_tag_type()}) {self.name}"

	class Meta:
		unique_together = ("name", "tag_type")


class TaxonTag(ReferencedModel):
	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE, db_index=True)

	class Meta:
		verbose_name_plural = "Taxon tags"
		unique_together = ["taxonomy"]


class Habitat(ReferencedModel):
	name = models.CharField(max_length=50, blank=False, unique=True)

	def __str__(self):
		return self.name


class IUCNData(ReferencedModel):
	# IUCN Assessment
	NE = 0  # Not Evaluated
	DD = 1  # Data Deficient
	LC = 2  # Least Concern
	NT = 3  # Near Threatened
	VU = 4  # Vulnerable
	EN = 5  # Endangered
	CR = 6  # Critically Endangered
	EW = 7  # Extinct in the Wild
	EX = 8  # Extinct
	CD = 9  # Conservation Dependent
	NA = 10  # Not Applicable

	# IUCN Region
	GLOBAL = 1
	EUROPE = 2
	MEDITERRANEAN = 3

	# Assessment choices
	CS_CHOICES = (
		(NE, "ne"),
		(DD, "dd"),
		(LC, "lc"),
		(NT, "nt"),
		(VU, "vu"),
		(EN, "en"),
		(CR, "cr"),
		(EW, "ew"),
		(EX, "ex"),
		(CD, "cd"),
		(NA, "na"),
	)

	# Region choices
	RG_CHOICES = (
		(GLOBAL, "global"),
		(EUROPE, "europe"),
		(MEDITERRANEAN, "mediterranean")
	)

	# Assessment translate
	TRANSLATE_CS = {
		NE: "ne",
		"ne": NE,
		DD: "dd",
		"dd": DD,
		LC: "lc",
		"lc": LC,
		NT: "nt",
		"nt": NT,
		VU: "vu",
		"vu": VU,
		EN: "en",
		"en": EN,
		CR: "cr",
		"cr": CR,
		EW: "ew",
		"ew": EW,
		EX: "ex",
		"ex": EX,
		CD: "cd",
		"cd": CD,
		NA: "na",
		"na": NA,
	}

	# Regional translate
	TRANSLATE_RG = {
		GLOBAL: "global",
		"global": GLOBAL,
		EUROPE: "europe",
		"europe": EUROPE,
		MEDITERRANEAN: "mediterranean",
		"mediterranean": MEDITERRANEAN
	}

	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	assessment = models.PositiveSmallIntegerField(choices=CS_CHOICES, default=NE)
	region = models.PositiveSmallIntegerField(choices=RG_CHOICES, default=None)
	# iucn_global = models.PositiveSmallIntegerField(choices=CS_CHOICES, default=NE)
	# iucn_europe = models.PositiveSmallIntegerField(choices=CS_CHOICES, default=NE)
	# iucn_mediterranean = models.PositiveSmallIntegerField(choices=CS_CHOICES, default=NE)
	# habitats = models.ManyToManyField(Habitat, blank=True, default=None)


	def __str__(self):
		return f"{self.taxonomy} - assessment: {self.assessment}, region: {self.region}"

	class Meta:
		verbose_name_plural = "IUCN"
		# Unique values for taxonomy and region. We cannot have a taxon with the same regions.
		unique_together = ["taxonomy", "region"]


class HabitatTaxonomy(ReferencedModel):
	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	habitat = models.ForeignKey(Habitat, on_delete=models.CASCADE, db_index=True)

	def __str__(self):
		return f"{self.taxonomy} - habitat: {self.habitat}"

	class Meta:
		verbose_name_plural = "Habitat Taxonomy"
		unique_together = ["taxonomy", "habitat"]  # Unique values for taxonomy and habitat.


class Directive(ReferencedModel):
	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	cites = models.BooleanField(default=None, null=True)
	ceea = models.BooleanField(default=None, null=True)
	lespre = models.BooleanField(default=None, null=True)
	directiva_aves = models.BooleanField(default=None, null=True)
	directiva_habitats = models.BooleanField(default=None, null=True)

	def __str__(self):
		return str(self.taxonomy)

	class Meta:
		unique_together = ["taxonomy"]
