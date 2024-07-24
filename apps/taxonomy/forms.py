from common.utils.forms import TranslateForm, CamelCaseForm
from django import forms

from common.utils.forms import IdFieldForm
from .models import TaxonomicLevel, Authorship


class TaxonomicLevelForm(IdFieldForm, TranslateForm):
	exact = forms.BooleanField(required=False)
	taxon_rank = forms.CharField(max_length=100, required=False)
	accepted = forms.NullBooleanField(required=False)
	authorship = forms.CharField(max_length=256, required=False)
	name = forms.CharField(required=False)
	rank = forms.IntegerField(required=False)  # assuming rank is stored as an integer
	sources = forms.CharField(required=False)
	unidecode_name = forms.CharField(required=False)

	TRANSLATE_FIELDS = {"taxon_rank": "rank", "scientific_name_authorship": "authorship"}

	CHOICES_FIELD = {"rank": TaxonomicLevel.TRANSLATE_RANK}


class TaxonomicLevelChildrenForm(IdFieldForm, CamelCaseForm):
	children_rank = forms.CharField(max_length=100, required=False)

	class Meta:
		fields = ["id", "children_rank"]


class AuthorshipForm(IdFieldForm):
	class Meta:
		fields = ["id"]
