from django.core.exceptions import ValidationError
from django.db import models
from unidecode import unidecode

from common.utils.utils import str_clean_up


class LatLonModel(models.Model):
	latitude = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
	longitude = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
	coordinatesUncertainty = models.PositiveIntegerField(null=True, blank=True)

	class Meta:
		abstract = True


class ReferencedModel(models.Model):
	references = models.ManyToManyField('versioning.Batch')
	sources = models.ManyToManyField('versioning.Source', blank=True)

	class Meta:
		abstract = True


class SynonymManager(models.Manager):
	def _override_args(self, kwargs):
		for arg in list(kwargs.keys()):
			if arg.startswith('name'):
				kwargs[arg] = str_clean_up(kwargs[arg])
				kwargs[f'unidecode_{arg}'] = unidecode(kwargs[arg])
				del kwargs[arg]

	def filter(self, *args, **kwargs):
		self._override_args(kwargs)
		return super().filter(**kwargs)

	def aggregate(self, *args, **kwargs):
		self._override_args(kwargs)
		return super().aggregate(*args, **kwargs)

	def get(self, *args, **kwargs):
		self._override_args(kwargs)
		return super().get(*args, **kwargs)

	def get_or_create(self, defaults=None, **kwargs):
		self._override_args(kwargs)
		return super().get_or_create(defaults, **kwargs)

	def create(self, **kwargs):
		self._override_args(kwargs)
		return super().create(**kwargs)

	def update_or_create(self, defaults=None, **kwargs):
		self._override_args(kwargs)
		return super().update_or_create(defaults, **kwargs)

	def update(self, **kwargs):
		self._override_args(kwargs)
		return super().update(**kwargs)

	def exclude(self, *args, **kwargs):
		self._override_args(kwargs)
		return super().exclude(*args, **kwargs)

	def alias(self, *args, **kwargs):
		self._override_args(kwargs)
		return super().alias(*args, **kwargs)

	def annotate(self, *args, **kwargs):
		self._override_args(kwargs)
		return super().annotate(*args, **kwargs)


class SynonymModel(models.Model):
	objects = SynonymManager()

	PROVISIONAL = 0
	AMBIGUOUS = 1
	MISAPPLIED = 2

	ACCEPTED_MODIFIERS_CHOICES = (
		(PROVISIONAL, 'provisional'),
		(AMBIGUOUS, 'provisional'),
		(MISAPPLIED, 'missaplied'),
	)
	ACCEPTED_MODIFIERS_TRANSLATE = {
		PROVISIONAL: 'provisional',
		'provisional': PROVISIONAL,
		AMBIGUOUS: 'ambiguous',
		'ambiguous': AMBIGUOUS,
		MISAPPLIED: 'misapplied',
		'misapplied': MISAPPLIED,
	}

	name = models.CharField(max_length=256)
	unidecode_name = models.CharField(max_length=256, help_text="Unidecode name do not touch")
	synonyms = models.ManyToManyField('self', blank=True, symmetrical=True)
	accepted = models.BooleanField(null=False, blank=False)
	accepted_modifier = models.PositiveSmallIntegerField(choices=ACCEPTED_MODIFIERS_CHOICES, null=True, blank=True, default=None)

	def clean(self):
		super().clean()
		n_accepted_syns = self.synonyms.all().filter(accepted=True).count() if self.id else 0

		if self.accepted:
			if n_accepted_syns != 0:
				raise ValidationError('No more than one synonym can be accepted')
		else:
			if n_accepted_syns == 0:
				raise ValidationError('At least one synonym must be accepted')
			if n_accepted_syns > 1:
				raise ValidationError('No more than one synonym can be accepted')

		if self.accepted_modifier:
			if self.accepted:
				if self.accepted_modifier not in [SynonymModel.PROVISIONAL]:
					raise ValidationError('Wrong modifier for accepted')
			else:  # synonym
				if self.accepted_modifier not in [SynonymModel.AMBIGUOUS, SynonymModel.MISAPPLIED]:
					raise ValidationError('Invalid modifier for synonym (accepted = False)')


	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.name = str_clean_up(self.name)
		self.unidecode_name = unidecode(self.name)
		super().save(force_insert, force_update, using, update_fields)

	def __str__(self):
		return str(self.name)

	def get_queryset_synonyms(self):
		return self.objects.all()

	class Meta:
		abstract = True
