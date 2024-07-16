from common.utils.forms import TranslateForm, CamelCaseForm
from django import forms
from django.forms import ModelForm

from common.utils.forms import IdFieldForm
from .models import TaxonomicLevel, Authorship


class TaxonomicLevelForm(IdFieldForm, TranslateForm):
	exact = forms.BooleanField(required=False)
	taxon_rank = forms.CharField(max_length=100, required=False)
	authorship = forms.CharField(max_length=256, required=False)
	TRANSLATE_FIELDS = {"taxon_rank": "rank", "scientific_name_authorship": "authorship"}
	CHOICES_FIELD = {"rank": TaxonomicLevel.TRANSLATE_RANK}

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


class TaxonomicLevelChildrenForm(IdFieldForm, CamelCaseForm):
	children_rank = forms.CharField(max_length=100, required=False)

	class Meta:
		model = TaxonomicLevel
		fields = ["id", "children_rank"]


class AuthorshipForm(IdFieldForm):
	class Meta:
		model = Authorship
		fields = ["id"]
