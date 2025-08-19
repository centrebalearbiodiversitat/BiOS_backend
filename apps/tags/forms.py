from django import forms
from humps import decamelize
from common.utils.forms import TranslateForm, CamelCaseForm

from .models import IUCNData
import re

class DirectiveForm(CamelCaseForm):
	cites = forms.BooleanField(required=False)
	ceea = forms.BooleanField(required=False)
	lespre = forms.BooleanField(required=False)
	directiva_aves = forms.BooleanField(required=False)
	directiva_habitats = forms.BooleanField(required=False)

	class Meta:
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		self.request_data = kwargs.get('data', None)
		super().__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super().clean()

		directive = self.request_data.get("directive", None)

		if directive == "cites":
			cleaned_data["cites"] = True
			return cleaned_data
		elif directive == "ceea":
			cleaned_data["ceea"] = True
			return cleaned_data
		elif directive == "lespre":
			cleaned_data["lespre"] = True
			return cleaned_data
		elif directive == "directiva_aves":
			cleaned_data["directiva_aves"] = True
			return cleaned_data
		elif directive == "directiva_habitats":
			cleaned_data["directiva_habitats"] = True
			return cleaned_data
		
class HabitatForm(TranslateForm):
	habitat = forms.CharField(max_length=50, required=False)


class IUCNDataForm(TranslateForm):
	assessment = forms.CharField(max_length=50, required=False)
	region = forms.CharField(max_length=100, required=False)

	TRANSLATE_FIELDS = {}
	CHOICES_FIELD = {
		"assessment": IUCNData.TRANSLATE_CS,
		"region": IUCNData.TRANSLATE_RG,
	}

	def __init__(self, *args, **kwargs):
		self.request_data = kwargs.get('data', None)
		super().__init__(*args, **kwargs)
	
	def clean(self):
		cleaned_data = super().clean()

		assessment = None
		region = None
		
		if self.request_data:

			for key, value in self.request_data.items():

				regex = r"iucn_.*"
				key = decamelize(key)
				region = key.replace("iucn_", "")

				if re.match(regex, key):
					assessment = IUCNData.TRANSLATE_CS.get(value)
					region = IUCNData.TRANSLATE_RG.get(region)
					break

			if assessment:
				cleaned_data['assessment'] = assessment
				cleaned_data['region'] = region
			
		return cleaned_data


class TaxonTagForm(CamelCaseForm):
	tag = forms.CharField(required=False)

	class Meta:
		fields = ["taxonomy", "tag"]


class SystemForm(CamelCaseForm):
	freshwater = forms.BooleanField(required=False)
	marine = forms.BooleanField(required=False)
	terrestrial = forms.BooleanField(required=False)
			
	def __init__(self, *args, **kwargs):
		self.request_data = kwargs.get('data', None)
		super().__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super().clean()

		system = self.request_data.get("system", None)

		if system == "marine":
			cleaned_data["marine"] = True
			return cleaned_data
		elif system == "freshwater":
			cleaned_data["freshwater"] = True
			return cleaned_data
		elif system == "terrestrial":
			cleaned_data["terrestrial"] = True
			return cleaned_data


	class Meta:
		fields = ["taxonomy", "freshwater", "marine", "terrestrial"]
			
	