from django import forms
from django.forms import ModelForm

from common.utils.forms import IdFieldForm
from .models import TaxonomicLevel, Authorship


class TaxonomicLevelForm(IdFieldForm):
	exact = forms.BooleanField(required=False)
	taxon_rank = forms.CharField(max_length=100, required=False)
	scientific_name_authorship = forms.CharField(max_length=256, required=False)

	class Meta:
		model = TaxonomicLevel
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["authorship"].required = False
		self.fields["batch"].required = False
		self.fields["name"].required = False
		self.fields["rank"].required = False
		self.fields["sources"].required = False
		self.fields["unidecode_name"].required = False

	def clean(self):
		cleaned_data = super().clean()

		if cleaned_data["taxon_rank"]:
			cleaned_data["taxon_rank"] = cleaned_data["taxon_rank"].lower()

			if cleaned_data["taxon_rank"] not in TaxonomicLevel.TRANSLATE_RANK:
				raise forms.ValidationError("Invalid rank")

			cleaned_data["rank"] = TaxonomicLevel.TRANSLATE_RANK[cleaned_data["taxon_rank"]]

		return cleaned_data


class AuthorshipForm(IdFieldForm):
	class Meta:
		model = Authorship
		fields = ["id"]
