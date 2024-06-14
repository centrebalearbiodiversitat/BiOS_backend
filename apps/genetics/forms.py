from common.utils.forms import CamelCaseForm, IdFieldForm
from .models import Gene, Product, Produces, GeneticFeatures
from django import forms


class GeneForm(IdFieldForm, CamelCaseForm):
	sources = forms.IntegerField(required=False)
	exact = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["batch"].required = False
		self.fields["name"].required = False
		self.fields["unidecode_name"].required = False
		self.fields["sources"].required = False

	class Meta:
		model = Gene
		fields = "__all__"


class ProductForm(IdFieldForm, CamelCaseForm):
	sources = forms.IntegerField(required=False)
	exact = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["batch"].required = False
		self.fields["name"].required = False
		self.fields["unidecode_name"].required = False
		self.fields["sources"].required = False

	class Meta:
		model = Product
		fields = "__all__"


class ProducesForm(IdFieldForm, CamelCaseForm):
	sources = forms.IntegerField(required=False)

	class Meta:
		model = Produces
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["batch"].required = False
		self.fields["sources"].required = False
		self.fields["gene"].required = False
		self.fields["product"].required = False


class GeneticFeaturesForm(IdFieldForm, CamelCaseForm):
	sources = forms.IntegerField(required=False)
	exact = forms.BooleanField(required=False)

	class Meta:
		model = GeneticFeatures
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["occurrence"].required = False
		self.fields["batch"].required = False
		self.fields["sources"].required = False
		self.fields["occurrence"].required = False
		self.fields["isolate"].required = False
		self.fields["bp"].required = False
		self.fields["definition"].required = False
		self.fields["data_file_division"].required = False
		self.fields["published_date"].required = False
		self.fields["collection_date_year"].required = False
		self.fields["collection_date_month"].required = False
		self.fields["collection_date_day"].required = False
		self.fields["molecule_type"].required = False
		self.fields["sequence_version"].required = False
		self.fields["products"].required = False
