from django import forms
from django.forms import ModelForm
from .models import TaxonomicLevel


class TaxonomicLevelForms(ModelForm):
	exact = forms.BooleanField(required=False)

	class Meta:
		model = TaxonomicLevel
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super(TaxonomicLevelForms, self).__init__(*args, **kwargs)
		self.fields['name'].required = False
		self.fields['rank'].required = False
		self.fields['references'].required = False
