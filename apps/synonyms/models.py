from django.db import models

# class TaxonIDs(models.Model):
# 	name = models.CharField(max_length=256, unique=True)


class SynonymAbstract(models.Model):
	name = models.CharField(max_length=256, unique=True)

	def clean(self):
		super().clean()
		self.name = " ".join(self.name.split())

	def __str__(self):
		return self.name

	class Meta:
		abstract = True


class Synonym(SynonymAbstract):
	pass


class AuthorSynonym(SynonymAbstract):
	pass
