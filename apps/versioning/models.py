from django.core.exceptions import ValidationError
from django.db import models


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
		verbose_name_plural = "batches"


class Basis(models.Model):
	internal_name = models.CharField(max_length=255, unique=True)
	name = models.CharField(max_length=255, blank=False)
	acronym = models.CharField(max_length=50, null=True, blank=True)
	url = models.URLField(null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	authors = models.TextField(null=True, blank=True)
	citation = models.TextField(null=True, blank=True)
	contact = models.CharField(max_length=255, null=True, blank=True)
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

	def get_name(self):
		return self.acronym or self.name or self.internal_name

	def __str__(self):
		return f"{self.get_name()}"

	class Meta:
		verbose_name_plural = "Bases"


class SourceManager(models.Manager):
	def get_queryset(self):
		qs = super().get_queryset()

		return qs.select_related("basis")


class Source(models.Model):
	objects = SourceManager()

	DATABASE = 0
	JOURNAL_ARTICLE = 1
	BOOK = 2
	WEB_PAGE = 3
	DOCUMENT = 4
	EXPERT = 5
	MUSEUM = 6

	SOURCE_TYPE_CHOICES = (
		(DATABASE, "database"),
		(JOURNAL_ARTICLE, "journal_article"),
		(BOOK, "book"),
		(WEB_PAGE, "web_page"),
		(DOCUMENT, "document"),
		(EXPERT, "expert"),
		(MUSEUM, "museum"),
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
		MUSEUM: "museum",
		"museum": MUSEUM,
	}
	SOURCE_TYPE_EXEMPT_OF_IDS = {
		JOURNAL_ARTICLE,
		BOOK,
		DOCUMENT,
		EXPERT,
		MUSEUM,
	}

	API = 0
	AI = 1
	EXPERT = 2
	PROVIDED = 3

	EXTRACTION_METHOD_CHOICES = (
		(API, "api"),
		(AI, "ai"),
		(EXPERT, "expert"),
		(PROVIDED, "provided"),
	)
	TRANSLATE_EXTRACTION_METHOD = {
		API: "api",
		"api": API,
		AI: "ai",
		"ai": AI,
		EXPERT: "expert",
		"expert": EXPERT,
		PROVIDED: "provided",
		"provided": PROVIDED,
	}

	TAXON = 0
	OCCURRENCE = 1
	SEQUENCE = 2
	IMAGE = 3
	TAXON_DATA = 4
	DATASET_KEY = 5

	DATA_TYPE_CHOICES = (
		(TAXON, "taxon"),
		(TAXON_DATA, "taxon_data"),
		(OCCURRENCE, "occurrence"),
		(SEQUENCE, "sequence"),
		(IMAGE, "image"),
		(DATASET_KEY, "dataset_key"),
	)
	TRANSLATE_DATA_TYPE = {
		TAXON: "taxon",
		OCCURRENCE: "occurrence",
		SEQUENCE: "sequence",
		IMAGE: "image",
		TAXON_DATA: "taxon_data",
		DATASET_KEY: "dataset_key",
		"taxon": TAXON,
		"occurrence": OCCURRENCE,
		"sequence": SEQUENCE,
		"image": IMAGE,
		"taxon_data": TAXON_DATA,
		"dataset_key": DATASET_KEY,
	}

	source_type = models.PositiveSmallIntegerField(choices=SOURCE_TYPE_CHOICES)
	extraction_method = models.PositiveSmallIntegerField(choices=EXTRACTION_METHOD_CHOICES)
	data_type = models.PositiveSmallIntegerField(choices=DATA_TYPE_CHOICES)
	url = models.URLField(null=True, blank=True, default=None)  # revisar
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, default=None)
	basis = models.ForeignKey(Basis, on_delete=models.CASCADE, related_name="source", null=True, blank=True, default=None)

	def clean(self):
		super().clean()
		if self.url and "{id}" not in self.url:
			raise ValidationError("Source: URL bad formatting. Missing '{id}'")

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.full_clean()
		super().save(force_insert, force_update, using, update_fields)

	def translate_source_type(self):
		return Source.TRANSLATE_SOURCE_TYPE[self.source_type]

	def translate_data_type(self):
		return Source.TRANSLATE_DATA_TYPE[self.data_type]

	def __str__(self):
		return f"{self.translate_data_type()}:{self.basis.get_name()}"

	class Meta:
		unique_together = ["basis", "data_type"]


class OriginId(models.Model):
	external_id = models.CharField(max_length=255, blank=True, null=True)
	source = models.ForeignKey(Source, on_delete=models.CASCADE, db_index=True)
	attribution = models.CharField(max_length=512, null=True, default=None, blank=True)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.clean()
		super().save(force_insert, force_update, using, update_fields)

	def clean(self):
		super().clean()
		if not self.external_id and self.source.source_type not in Source.SOURCE_TYPE_EXEMPT_OF_IDS:
			raise ValidationError(f"External ID is None and is not allowed with origin type '{self.source.translate_source_type().upper()}'")

	def __str__(self):
		if self.external_id:
			return f"{self.source.basis.internal_name}:{self.external_id}"
		else:
			return f"{self.source.basis.internal_name}"

	class Meta:
		indexes = [
			models.Index(fields=["external_id", "source"]),
		]
		unique_together = ("external_id", "source")
