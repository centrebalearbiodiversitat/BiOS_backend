from django.db import models


class ModelWithSynonyms(models.Model):
	SYNONYMS_FILTERS = {
		'rank': 0
	}
	name = models.CharField(max_length=256)
	synonyms = models.ManyToManyField('self', blank=True)
	accepted = models.BooleanField(null=False, blank=False)

	def __str__(self):
		return str(self.name)

	def get_queryset_synonyms(self):
		return self.objects.all()

	class Meta:
		abstract = True
