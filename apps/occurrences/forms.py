from django import forms

from common.utils.forms import TranslateForm, IdFieldForm, CamelCaseForm
from .models import Occurrence
from django import forms

BALEARIC_ISLANDS = 1


class OccurrenceForm(IdFieldForm, TranslateForm):
	TRANSLATE_FIELDS = {
		"year": "collection_date_year",
		"month": "collection_date_month",
		"day": "collection_date_day",
	}

	taxonomy = forms.IntegerField(required=False)
	voucher = forms.CharField(required=False)
	geographical_location = forms.CharField(required=False, initial=BALEARIC_ISLANDS)
	collection_date_year = forms.IntegerField(required=False)
	collection_date_month = forms.IntegerField(required=False)
	collection_date_day = forms.IntegerField(required=False)
	basis_of_record = forms.CharField(required=False)
	batch = forms.CharField(required=False)
	sources = forms.CharField(required=False)

	add_synonyms = forms.BooleanField(required=False, initial=True)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
