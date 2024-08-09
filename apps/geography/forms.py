from django import forms
from .models import GeographicLevel
from common.utils.forms import TranslateForm


class GeographicLevelForm(TranslateForm):
	rank = forms.CharField(max_length=100, required=False)
	exact = forms.BooleanField(required=False)
	id = forms.IntegerField(error_messages={"invalid": "ID must be an integer"}, required=False)
	parent = forms.IntegerField(error_messages={"invalid": "Parent ID must be an integer"}, required=False)
	name = forms.CharField(required=False)
	unidecode_name = forms.CharField(required=False)

	CHOICES_FIELD = {"rank": GeographicLevel.TRANSLATE_RANK}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def clean_parent(self):
		parent = self.cleaned_data.get("parent")
		if parent:
			try:
				parent_instance = GeographicLevel.objects.get(id=parent)
				return parent_instance
			except GeographicLevel.DoesNotExist:
				raise forms.ValidationError("Parent ID does not exist.")
		return None
