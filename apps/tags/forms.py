from django import forms

from common.utils.forms import IdFieldForm, TranslateForm

from .models import IUCNData, System, TaxonTag


class DirectiveForm(IdFieldForm, TranslateForm):
	taxonomy = forms.IntegerField(required=False)

	class Meta:
		model = TaxonTag
		fields = ["taxonomy"]


class IUCNDataForm(IdFieldForm, TranslateForm):
	taxonomy = forms.IntegerField(required=False)
	iucn_global = forms.CharField(max_length=100, required=False)
	iucn_europe = forms.CharField(max_length=100, required=False)
	iucn_mediterranean = forms.CharField(max_length=100, required=False)
	habitat = forms.IntegerField(required=False)

	CHOICES_FIELD = {
		"iucn_global": IUCNData.TRANSLATE_CS,
		"iucn_europe": IUCNData.TRANSLATE_CS,
		"iucn_mediterranean": IUCNData.TRANSLATE_CS,
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class TaxonTagForm(IdFieldForm, TranslateForm):
	taxonomy = forms.IntegerField(required=False)

	class Meta:
		model = TaxonTag
		fields = ["taxonomy"]


class SystemForm(IdFieldForm, TranslateForm):
	taxonomy = forms.IntegerField(required=False)

	class Meta:
		model = System
		fields = ["taxonomy", "freshwater", "marine", "terrestrial"]
