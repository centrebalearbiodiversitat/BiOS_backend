from apps.geography.models import GeographicLevel
from common.utils.forms import TranslateForm, IdFieldForm
from django import forms


class OccurrenceForm(IdFieldForm, TranslateForm):
	TRANSLATE_FIELDS = {
		"year": "collection_date_year",
		"month": "collection_date_month",
		"day": "collection_date_day",
	}

	taxonomy = forms.IntegerField(required=False)
	voucher = forms.CharField(required=False)
	geographical_location = forms.CharField(required=False, initial=GeographicLevel.DEFAULT_BALEARIC_ISLANDS_ID)
	collection_date_year = forms.IntegerField(required=False)
	collection_date_month = forms.IntegerField(required=False)
	collection_date_day = forms.IntegerField(required=False)
	basis_of_record = forms.CharField(required=False)
	batch = forms.CharField(required=False)
	sources = forms.CharField(required=False)

	add_synonyms = forms.BooleanField(required=False, initial=True)
