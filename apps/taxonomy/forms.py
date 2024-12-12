from django import forms

from common.utils.forms import CamelCaseForm, IdFieldForm, TranslateForm, PaginatorFieldForm

from .models import TaxonomicLevel


class TaxonomicLevelForm(IdFieldForm, TranslateForm):
	exact = forms.BooleanField(required=False)
	rank = forms.CharField(max_length=100, required=False)
	authorship = forms.CharField(max_length=256, required=False)
	name = forms.CharField(required=False)
	accepted = forms.NullBooleanField(required=False)
	has_image = forms.NullBooleanField(required=False)
	ancestor_id = forms.IntegerField(required=False)

	TRANSLATE_FIELDS = {
		"taxon_rank": "rank",
		"scientific_name_authorship": "authorship"
	}
	CHOICES_FIELD = {"rank": TaxonomicLevel.TRANSLATE_RANK}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class ListTaxonomicLevelForm(PaginatorFieldForm, TaxonomicLevelForm):
	pass


class TaxonomicLevelChildrenForm(IdFieldForm, CamelCaseForm):
	children_rank = forms.CharField(max_length=100, required=False)
	accepted_only = forms.NullBooleanField(required=False)
