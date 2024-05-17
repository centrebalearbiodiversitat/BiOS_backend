from django.forms import ModelForm
from .models import Occurrence, TaxonomicLevel, GeographicLevel

class OccurrenceForm(ModelForm):

	class Meta:
		model = Occurrence
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["taxonomy"].required = False
		self.fields["voucher"].required = False
		self.fields["geographical_location"].required = False
		self.fields["collection_date_year"].required = False
		self.fields["collection_date_month"].required = False
		self.fields["collection_date_day"].required = False
		self.fields["basis_of_record"].required = False
		self.fields["batch"].required = False
		self.fields["sources"].required = False