from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
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
	DIRECTIVE = 1

	TAG_TYPE_CHOICES = (
		(DOE, "degreeOfEstablishment"),
		(DIRECTIVE, "directive"),
	)

	TRANSLATE_TYPE = {
		"degreeOfEstablishment": DOE,
		DOE: "degreeOfEstablishment",
		"directive": DIRECTIVE,
		DIRECTIVE: "directive",
	}

	name = models.CharField(max_length=255)
	tag_type = models.PositiveSmallIntegerField(choices=TAG_TYPE_CHOICES)

	class Meta:
		unique_together = ("name", "tag_type")

	def __str__(self):
		return f"{self.name}"


class TaxonTag(ReferencedModel):
	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True)
	tags = models.ManyToManyField(Tag, blank=True)

	class Meta:
		verbose_name_plural = "Taxon tags"
		unique_together = ["taxonomy"]


@receiver(m2m_changed, sender=TaxonTag.tags.through)
def validate_doe_tag(instance, action, **kwargs):
	if action == "post_add":
		if instance.tags.filter(tag_type=Tag.DOE).count() > 1:
			raise ValueError("You cannot add another DOE Tag. There is already one associated with it.")


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
	habitat = models.ManyToManyField(Habitat, blank=True)

	def __str__(self):
		return f"{self.taxonomy} - iucn_global: {self.iucn_global}, iucn_europe: {self.iucn_europe}, iucn_mediterranean: {self.iucn_mediterranean}, habitat: {self.habitat}"

	class Meta:
		verbose_name_plural = "IUCN data"
		unique_together = ["taxonomy"]


class Directive(ReferencedModel):
	taxon_name = models.CharField(max_length=50, unique=True)
	taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE, db_index=True, null=True)
	cites = models.BooleanField(default=None, null=True)
	ceea = models.BooleanField(default=None, null=True)
	lespre = models.BooleanField(default=None, null=True)
	directiva_aves = models.BooleanField(default=None, null=True)
	directiva_habitats = models.BooleanField(default=None, null=True)

	def __str__(self):
		return self.taxon_name

	class Meta:
		unique_together = ["taxon_name"]
