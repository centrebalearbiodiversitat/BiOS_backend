from common.utils.forms import CamelCaseForm
from .models import Occurrence


class OccurrenceForm(CamelCaseForm):
	TRANSLATE_FIELDS = {
		"year": "collection_date_year",
		"month": "collection_date_month",
		"day": "collection_date_day",
	}

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

	class Meta:
		model = Occurrence
		fields = "__all__"
