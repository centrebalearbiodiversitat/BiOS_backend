from django.core.exceptions import ValidationError
from django.db import models
import sys

class Batch(models.Model):
	PENDING = 0
	ACCEPTED = 1
	REJECTED = 2
	STATUS_CHOICES = (
		(PENDING, "Pending"),
		(ACCEPTED, "Accepted"),
		(REJECTED, "Rejected"),
	)

	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)

	def __str__(self):
		return f"{self.created_at.year}-{self.created_at.month}-{self.created_at.day}__{self.id}"

	class Meta:
		app_label = "versioning"
		verbose_name_plural = "batches"


class Source(models.Model):
	internal_name = models.CharField(max_length=255, unique=True)
	name = models.CharField(max_length=255, blank=False)
	acronym = models.CharField(max_length=50, null=True, blank=True)
	url = models.URLField(null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	authors = models.ManyToManyField("taxonomy.Authorship", blank=True)
	citation = models.TextField(null=True, blank=True)
	contact = models.CharField(max_length=255, null=True, blank=True)
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, default=None)


	def __str__(self):
		return f"Information for {self.name}"


class Module(models.Model):
	DATABASE = 0
	JOURNAL_ARTICLE = 1
	BOOK = 2
	WEB_PAGE = 3
	DOCUMENT = 4
	EXPERT = 5

	SOURCE_TYPE_CHOICES = (
		(DATABASE, "database"),
		(JOURNAL_ARTICLE, "journal_article"),
		(BOOK, "book"),
		(WEB_PAGE, "web_page"),
		(DOCUMENT, "document"),
		(EXPERT, "expert"),
	)
	TRANSLATE_SOURCE_TYPE = {
		DATABASE: "database",
		"database": DATABASE,
		JOURNAL_ARTICLE: "journal_article",
		"journal_article": JOURNAL_ARTICLE,
		BOOK: "book",
		"book": BOOK,
		WEB_PAGE: "web_page",
		"web_page": WEB_PAGE,
		DOCUMENT: "document",
		"document": DOCUMENT,
		EXPERT: "expert",
		"expert": EXPERT,
	}

	API = 0
	AI = 1
	EXPERT = 2

	EXTRACTION_METHOD_CHOICES = (
		(API, "api"),
		(AI, "ai"),
		(EXPERT, "expert"),
	)
	TRANSLATE_EXTRACTION_METHOD = {
		API: "api",
		"api": API,
		AI: "ai",
		"ai": AI,
		EXPERT: "expert",
		"expert": EXPERT,
	}

	TAXON = 0
	OCCURRENCE = 1
	SEQUENCE = 2
	IMAGE = 3
	TAXON_DATA = 4
	DATA_TYPE_CHOICES = (
		(TAXON, "taxon"),
		(TAXON_DATA, "taxon_data"),
		(OCCURRENCE, "occurrence"),
		(SEQUENCE, "sequence"),
		(IMAGE, "image"),
	)
	TRANSLATE_DATA_TYPE = {
		TAXON: "taxon",
		OCCURRENCE: "occurrence",
		SEQUENCE: "sequence",
		IMAGE: "image",
		TAXON_DATA: "taxon_data",
		"taxon": TAXON,
		"occurrence": OCCURRENCE,
		"sequence": SEQUENCE,
		"image": IMAGE,
		"taxon_data": TAXON_DATA,
	}
	
	source_type = models.PositiveSmallIntegerField(choices=SOURCE_TYPE_CHOICES)
	extraction_method = models.PositiveSmallIntegerField(choices=EXTRACTION_METHOD_CHOICES)
	data_type = models.PositiveSmallIntegerField(choices=DATA_TYPE_CHOICES)
	url = models.URLField(null=True, blank=True, default=None) #revisar
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, default=None)
	source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='module')


	def __str__(self):
		return self.source.name


class OriginId(models.Model):
	external_id = models.CharField(max_length=255, blank=True, null=True)
	module = models.ForeignKey(Module, on_delete=models.CASCADE, db_index=True)
	attribution = models.CharField(max_length=512, null=True, default=None, blank=True)

	def clean(self):
		super().clean()
		if self.external_id:
			if OriginId.objects.filter(external_id=self.external_id, module=self.module).exists():
				raise ValidationError("External ID already exists for this source.")
		elif self.module.external_id in {Module.DATABASE, Module.JOURNAL_ARTICLE, Module.WEB_PAGE}:
			raise ValidationError(f"External ID is None and is not allowed with origin type '{Module.TRANSLATE_CHOICES[self.module.source_type].upper()}'")

	def __str__(self):
		return f"{self.module.source.internal_name}:{self.external_id}"

	class Meta:
		indexes = [
			models.Index(fields=["external_id", "module"]),
		]
