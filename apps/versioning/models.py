from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Upper


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
	DATABASE = 0
	JOURNAL_ARTICLE = 1
	BOOK = 2
	WEB_PAGE = 3
	DOCUMENT = 4
	EXPERT = 5
	MUSEUM = 6

	TYPE_CHOICES = (
		(DATABASE, "database"),
		(JOURNAL_ARTICLE, "journal_article"),
		(BOOK, "book"),
		(WEB_PAGE, "web_page"),
		(DOCUMENT, "document"),
		(EXPERT, "expert"),
		(MUSEUM, "museum"),
	)
	TRANSLATE_TYPE = {
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
	TYPE_EXEMPT_OF_IDS = {
		JOURNAL_ARTICLE,
		BOOK,
		DOCUMENT,
		EXPERT,
		MUSEUM,
	}

	internal_name = models.CharField(max_length=255, unique=True)
	name = models.CharField(max_length=1023, blank=True, null=True)
	acronym = models.CharField(max_length=50, null=True, blank=True)
	type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
	url = models.URLField(null=True, blank=True)
	image = models.URLField(null=True, max_length=255, blank=True)
	description = models.TextField(null=True, blank=True)
	authors = models.TextField(null=True, blank=True)
	citation = models.TextField(null=True, blank=True)
	contact = models.CharField(max_length=255, null=True, blank=True)
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

	def get_name(self):
		return self.name or self.internal_name

	def translate_type(self):
		return Basis.TRANSLATE_TYPE[self.type]

	def __str__(self):
		return f"{self.get_name()}"

	class Meta:
		verbose_name_plural = "Bases"
		indexes = [
			models.Index(Upper('internal_name'), name='basis_internal_name_upper_idx'),
		]


class SourceManager(models.Manager):
	def get_queryset(self):
		qs = super().get_queryset()

		return qs.select_related("basis")


class Source(models.Model):
	objects = SourceManager()

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

	extraction_method = models.PositiveSmallIntegerField(choices=EXTRACTION_METHOD_CHOICES)
	data_type = models.PositiveSmallIntegerField(choices=DATA_TYPE_CHOICES)
	url = models.URLField(null=True, blank=True, default=None)  # revisar
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, default=None)
	basis = models.ForeignKey(Basis, on_delete=models.CASCADE, related_name="source", null=True, blank=True, default=None, db_index=True)

	def clean(self):
		super().clean()
		if self.url and "{id}" not in self.url:
			raise ValidationError("Source: URL bad formatting. Missing '{id}'")

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.full_clean()
		super().save(force_insert, force_update, using, update_fields)

	def translate_data_type(self):
		return Source.TRANSLATE_DATA_TYPE[self.data_type]

	def __str__(self):
		return f"{self.translate_data_type()}:{self.basis.get_name()}"

	class Meta:
		unique_together = ["basis", "data_type"]
		indexes = [
			models.Index(fields=["basis"]),
			models.Index(fields=["id", "basis"]),
			models.Index(fields=["basis", "data_type"]),
		]


class OriginId(models.Model):
	external_id = models.CharField(max_length=255, blank=True, null=True)
	source = models.ForeignKey(Source, on_delete=models.CASCADE)
	attribution = models.CharField(max_length=512, null=True, default=None, blank=True)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.clean()
		super().save(force_insert, force_update, using, update_fields)

	def clean(self):
		super().clean()
		if not self.external_id and self.source.basis.type not in Basis.TYPE_EXEMPT_OF_IDS:
			raise ValidationError(f"External ID is None and is not allowed with origin type '{self.source.basis.translate_type().upper()}'")

	def __str__(self):
		if self.external_id:
			return f"{self.source.basis.internal_name}:{self.external_id}"
		else:
			return f"{self.source.basis.internal_name}"

	class Meta:
		indexes = [
			models.Index(fields=["source_id"]),
			models.Index(fields=["external_id", "source"]),
			models.Index(Upper('external_id'), name='originid_external_id_upper_idx'),
		]
		unique_together = ("external_id", "source")
