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
	NE = 0
	DD = 1
	LC = 2
	NT = 3
	VU = 4
	EN = 5
	CR = 6
	EW = 7
	EX = 8
	CD = 9
	NA = 10

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

	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	iucn_global = models.PositiveSmallIntegerField(choices=CS_CHOICES, default=NE)
	iucn_europe = models.PositiveSmallIntegerField(choices=CS_CHOICES, default=NE)
	iucn_mediterranean = models.PositiveSmallIntegerField(choices=CS_CHOICES, default=NE)
	habitats = models.ManyToManyField(Habitat, blank=True, default=None)

	def __str__(self):
		return f"{self.taxonomy} - iucn_global: {self.iucn_global}, iucn_europe: {self.iucn_europe}, iucn_mediterranean: {self.iucn_mediterranean}"

	class Meta:
		verbose_name_plural = "IUCN data"
		unique_together = ["taxonomy"]


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
