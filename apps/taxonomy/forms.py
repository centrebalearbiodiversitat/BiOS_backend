from django import forms

from common.utils.forms import CamelCaseForm, IdFieldForm, TranslateForm, PaginatorFieldForm

from .models import TaxonomicLevel
from apps.tags.models import IUCNData



class TaxonomicLevelForm(IdFieldForm, TranslateForm):
	exact = forms.BooleanField(required=False)
	rank = forms.CharField(max_length=100, required=False)
	authorship = forms.CharField(max_length=256, required=False)
	name = forms.CharField(required=False)
	accepted = forms.NullBooleanField(required=False)
	has_image = forms.NullBooleanField(required=False)
	ancestor_id = forms.IntegerField(required=False)

	# Advanced search fields
	iucn_global = forms.CharField(required=False)
	iucn_europe = forms.CharField(required=False)
	iucn_mediterranean = forms.CharField(required=False)
	cites = forms.BooleanField(required=False)
	ceea = forms.BooleanField(required=False)
	lespre = forms.BooleanField(required=False)
	directiva_aves = forms.BooleanField(required=False)
	directiva_habitats = forms.BooleanField(required=False)
	freshwater = forms.BooleanField(required=False)
	marine = forms.BooleanField(required=False)
	terrestrial = forms.BooleanField(required=False)
	taxon_tag = forms.IntegerField(required=False)
	source = forms.CharField(required=False)

	TRANSLATE_FIELDS = {"taxon_rank": "rank", "scientific_name_authorship": "authorship"}
	CHOICES_FIELD = {"rank": TaxonomicLevel.TRANSLATE_RANK}

	def clean_iucn_field(self, field_name):
		value = self.cleaned_data.get(field_name)
		if value:
			try:
				return IUCNData.TRANSLATE_CS[value.lower()]
			except KeyError:
				raise forms.ValidationError(f"Invalid value for {field_name}")
		return None

	def clean(self):
		cleaned_data = super().clean()

		for field_name in ['cites', 'ceea', 'lespre', 'directiva_aves', 'directiva_habitats', 'freshwater', 'marine', 'terrestrial']:
			if field_name not in self.data:
				cleaned_data[field_name] = None

		for field_name in ['iucn_global', 'iucn_europe', 'iucn_mediterranean']:
			cleaned_data[field_name] = self.clean_iucn_field(field_name)

		return cleaned_data

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class ListTaxonomicLevelForm(PaginatorFieldForm, TaxonomicLevelForm):
	pass


class TaxonomicLevelChildrenForm(IdFieldForm, CamelCaseForm):
	children_rank = forms.CharField(max_length=100, required=False)
	accepted_only = forms.NullBooleanField(required=False)
