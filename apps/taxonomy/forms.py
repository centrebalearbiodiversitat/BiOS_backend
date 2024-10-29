from django import forms

from common.utils.forms import CamelCaseForm, IdFieldForm, TranslateForm

from .models import TaxonData, TaxonomicLevel


class TaxonomicLevelForm(IdFieldForm, TranslateForm):
	exact = forms.BooleanField(required=False)
	rank = forms.CharField(max_length=100, required=False)
	authorship = forms.CharField(max_length=256, required=False)
	name = forms.CharField(required=False)
	accepted = forms.NullBooleanField(required=False)

	TRANSLATE_FIELDS = {"taxon_rank": "rank", "scientific_name_authorship": "authorship"}
	CHOICES_FIELD = {"rank": TaxonomicLevel.TRANSLATE_RANK}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class TaxonomicLevelChildrenForm(IdFieldForm, CamelCaseForm):
	children_rank = forms.CharField(max_length=100, required=False)
	accepted_only = forms.NullBooleanField(required=False)


class TaxonDataForm(IdFieldForm, TranslateForm):
	taxonomy = forms.IntegerField(required=False)
	iucn_global = forms.CharField(max_length=100, required=False)
	iucn_europe = forms.CharField(max_length=100, required=False)
	iucn_mediterranean = forms.CharField(max_length=100, required=False)
	invasive = forms.NullBooleanField(required=False)
	domesticated = forms.NullBooleanField(required=False)
	freshwater = forms.NullBooleanField(required=False)
	marine = forms.NullBooleanField(required=False)
	terrestrial = forms.NullBooleanField(required=False)

	CHOICES_FIELD = {
		"iucn_global": TaxonData.TRANSLATE_CS,
		"iucn_europe": TaxonData.TRANSLATE_CS,
		"iucn_mediterranean": TaxonData.TRANSLATE_CS,
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class TagForm(IdFieldForm, TranslateForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
