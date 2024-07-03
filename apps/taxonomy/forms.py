from common.utils.forms import TranslateForm
from django import forms

from common.utils.forms import IdFieldForm
from .models import TaxonomicLevel, Authorship


class TaxonomicLevelForm(IdFieldForm, TranslateForm):
	exact = forms.BooleanField(required=False)
	synonyms = forms.IntegerField(required=False)
	taxon_rank = forms.CharField(max_length=100, required=False)
	accepted = forms.BooleanField(required=False)
	authorship = forms.CharField(max_length=256, required=False)
	name = forms.CharField(required=False)
	rank = forms.IntegerField(required=False)  # assuming rank is stored as an integer
	sources = forms.CharField(required=False)
	unidecode_name = forms.CharField(required=False)

	TRANSLATE_FIELDS = {"taxon_rank": "rank", "scientific_name_authorship": "authorship"}

	CHOICES_FIELD = {"rank": TaxonomicLevel.TRANSLATE_RANK}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class AuthorshipForm(IdFieldForm):
	class Meta:
		model = Authorship
		fields = ["id"]
