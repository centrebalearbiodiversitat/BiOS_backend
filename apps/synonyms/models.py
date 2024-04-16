from django.core.exceptions import ValidationError
from django.db import models


class ModelWithSynonyms(models.Model):
	SYNONYMS_FILTERS = {
		'rank': 0
	}
	name = models.CharField(max_length=256)
	synonyms = models.ManyToManyField('self', blank=True)
	accepted = models.BooleanField(null=False, blank=False)

	def clean(self):
		super().clean()
		n_accepted_syns = self.synonyms.all().filter(accepted=True).count()

		if self.accepted:
			if n_accepted_syns != 0:
				raise ValidationError('No more than one synonym can be accepted')
		else:
			if n_accepted_syns == 0:
				raise ValidationError('At least one synonym must be accepted')
			if n_accepted_syns > 1:
				raise ValidationError('No more than one synonym can be accepted')

	def __str__(self):
		return str(self.name)

	def get_queryset_synonyms(self):
		return self.objects.all()

	class Meta:
		abstract = True
