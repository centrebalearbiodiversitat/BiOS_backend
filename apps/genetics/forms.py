from django import forms

from common.utils.forms import CamelCaseForm, IdFieldForm, InGeographyScopeForm


class MarkerForm(IdFieldForm, InGeographyScopeForm):
	sources = forms.IntegerField(required=False)
	exact = forms.BooleanField(required=False)
	batch = forms.CharField(required=False)
	name = forms.CharField(required=False)
	unidecode_name = forms.CharField(required=False)
	taxonomy = forms.IntegerField(required=False)


class SequenceForm(IdFieldForm, CamelCaseForm):
	sources = forms.IntegerField(required=False)
	exact = forms.BooleanField(required=False)
	occurrence = forms.CharField(required=False)
	batch = forms.CharField(required=False)
	isolate = forms.CharField(required=False)
	bp = forms.CharField(required=False)
	definition = forms.CharField(required=False)
	data_file_division = forms.CharField(required=False)
	published_date = forms.DateField(required=False)
	molecule_type = forms.CharField(required=False)
	sequence_version = forms.CharField(required=False)
	products = forms.CharField(required=False)


class SequenceListForm(InGeographyScopeForm):
	taxonomy = forms.IntegerField(required=False)
	marker = forms.IntegerField(required=False)
