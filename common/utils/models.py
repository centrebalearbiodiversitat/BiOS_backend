from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from unidecode import unidecode

from common.utils.utils import str_clean_up


class LatLonModel(models.Model):
	latitude = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
	longitude = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
	coordinatesUncertaintyMeters = models.PositiveIntegerField(null=True, blank=True)
	elevationMeters = models.IntegerField(null=True, blank=True, default=True)
	depthMeters = models.IntegerField(null=True, blank=True, default=True)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		if not (
			(self.latitude is not None and self.longitude is not None) or (self.latitude == self.longitude == None)
		):
			raise ValidationError("Latitude and longitude must both exist or None")
		super().save(force_insert, force_update, using, update_fields)

	class Meta:
		abstract = True


class ReferencedModel(models.Model):
	batch = models.ForeignKey("versioning.Batch", on_delete=models.CASCADE)
	sources = models.ManyToManyField("versioning.OriginSource")

	@staticmethod
	def clean_sources(**kwargs):
		if kwargs and kwargs["action"] == "post_add":
			obj = kwargs["instance"]

			sources = [s.source.name for s in obj.sources.all()]

			if len(sources) != len(set(sources)):
				raise ValidationError(f"Sources must be unique.\n{obj}\n{sources}")

	class Meta:
		abstract = True


m2m_changed.connect(ReferencedModel.clean_sources, sender=ReferencedModel.sources.through)


class SynonymManager(models.Manager):
	def _override_args(self, kwargs):
		for arg in list(kwargs.keys()):
			if arg.startswith("name"):
				kwargs[arg] = str_clean_up(kwargs[arg])
				kwargs[f"unidecode_{arg}"] = unidecode(kwargs[arg])
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
		(PROVISIONAL, "Provisional"),
		(AMBIGUOUS, "Ambiguous"),
		(MISAPPLIED, "Misaplied"),
	)
	ACCEPTED_MODIFIERS_TRANSLATE = {
		PROVISIONAL: "provisional",
		"provisional": PROVISIONAL,
		AMBIGUOUS: "ambiguous",
		"ambiguous": AMBIGUOUS,
		MISAPPLIED: "misapplied",
		"misapplied": MISAPPLIED,
	}

	name = models.CharField(max_length=256)
	unidecode_name = models.CharField(max_length=256, help_text="Unidecode name do not touch")
	synonyms = models.ManyToManyField("self", blank=True, symmetrical=True)
	accepted = models.BooleanField(null=False, blank=False)
	accepted_modifier = models.PositiveSmallIntegerField(
		choices=ACCEPTED_MODIFIERS_CHOICES, null=True, blank=True, default=None
	)

	@staticmethod
	def clean_synonyms(**kwargs):
		if kwargs and kwargs["action"] == "post_add":
			obj = kwargs["instance"]

			if not hasattr(obj, "synonyms"):
				return

			syns = obj.synonyms.all()

			if obj.id and syns.filter(id=obj.id).exists():
				raise ValidationError(f"Self synonym is not allowed.\n{obj}\n{syns}")

			n_accepted_syns = syns.filter(accepted=True).count()

			if obj.accepted:
				if n_accepted_syns != 0:
					raise ValidationError(f"No more than one synonym can be accepted.\n{obj}\n{syns}")
			else:
				# if n_accepted_syns == 0:
				# 	print(obj, syns)
				# 	raise ValidationError(f'At least one synonym must be accepted.\n{obj}\n{syns}')
				if n_accepted_syns > 1:
					raise ValidationError(f"No more than one synonym can be accepted.\n{obj}\n{syns}")

			if obj.accepted_modifier:
				if obj.accepted:
					if obj.accepted_modifier not in [SynonymModel.PROVISIONAL]:
						raise ValidationError(f"Wrong modifier for accepted\n{obj}\n{syns}")
				else:  # synonym
					if obj.accepted_modifier not in [SynonymModel.AMBIGUOUS, SynonymModel.MISAPPLIED]:
						raise ValidationError(f"Invalid modifier for synonym (accepted = False)\n{obj}\n{syns}")

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


m2m_changed.connect(SynonymModel.clean_synonyms, sender=SynonymModel.synonyms.through)
