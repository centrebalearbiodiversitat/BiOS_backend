from django.core.exceptions import ValidationError
from django.db import models

from common.utils.models import SynonymModel


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


class Source(SynonymModel):
	DATABASE = 0
	JOURNAL_ARTICLE = 1
	BOOK = 2
	AI = 3
	WEB_PAGE = 4
	DOCUMENT = 5
	EXPERT = 6

	ORIGIN_CHOICES = (
		(DATABASE, "database"),
		(JOURNAL_ARTICLE, "journal_article"),
		(BOOK, "book"),
		(AI, "ai"),
		(WEB_PAGE, "web_page"),
		(DOCUMENT, "document"),
		(EXPERT, "expert"),
	)
	TRANSLATE_CHOICES = {
		DATABASE: "database",
		"database": DATABASE,
		JOURNAL_ARTICLE: "journal_article",
		"journal_article": JOURNAL_ARTICLE,
		BOOK: "book",
		"book": BOOK,
		AI: "ai",
		"ai": AI,
		WEB_PAGE: "web_page",
		"web_page": WEB_PAGE,
		DOCUMENT: "document",
		"document": DOCUMENT,
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

	origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES)
	url = models.URLField(null=True, blank=True, default=None)
	data_type = models.PositiveSmallIntegerField(choices=DATA_TYPE_CHOICES)
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, default=None)

	def __str__(self):
		return self.name


class OriginSource(models.Model):
	origin_id = models.CharField(max_length=255, blank=False, null=False)
	source = models.ForeignKey(Source, on_delete=models.CASCADE, db_index=True)
	attribution = models.CharField(max_length=512, null=True, default=None, blank=True)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		super().save(force_insert, force_update, using, update_fields)
		if not self.origin_id:
			raise ValidationError('Blank "origin_id" field is not allowed.')

	def __str__(self):
		return f"{self.source.name}:{self.origin_id}"

	class Meta:
		unique_together = ("origin_id", "source")
		indexes = [
			models.Index(fields=["id", "source"]),
		]
