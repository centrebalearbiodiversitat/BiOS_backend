from django import forms
from common.utils.forms import IdFieldForm, TranslateForm, CamelCaseForm


class LatLonModelForm(IdFieldForm, TranslateForm):
	decimal_latitude_min = forms.DecimalField(max_digits=8, decimal_places=5, required=False, label="Minimum Latitude")
	decimal_latitude_max = forms.DecimalField(max_digits=8, decimal_places=5, required=False, label="Maximum Latitude")
	decimal_longitude_min = forms.DecimalField(max_digits=8, decimal_places=5, required=False, label="Minimum Longitude")
	decimal_longitude_max = forms.DecimalField(max_digits=8, decimal_places=5, required=False, label="Maximum Longitude")
	coordinate_uncertainty_in_meters_min = forms.IntegerField(required=False, min_value=0, label="Minimum Coordinate Uncertainty (meters)")
	coordinate_uncertainty_in_meters_max = forms.IntegerField(required=False, min_value=0, label="Maximum Coordinate Uncertainty (meters)")
	elevation_min = forms.IntegerField(required=False, label="Minimum Elevation")
	elevation_max = forms.IntegerField(required=False, label="Maximum Elevation")
	depth_min = forms.IntegerField(required=False, label="Minimum Depth")
	depth_max = forms.IntegerField(required=False, label="Maximum Depth")

	def clean(self):
		cleaned_data = super().clean()

		# Change key names into the dictionary
		# cleaned_data["coordinate_uncertainty_in_meters_min"] = cleaned_data.pop("uncertainty_min", None)
		# cleaned_data["coordinate_uncertainty_in_meters_max"] = cleaned_data.pop("uncertainty_max", None)

		coordinate_uncertainty_in_meters_min = cleaned_data.get("coordinate_uncertainty_in_meters_min")
		coordinate_uncertainty_in_meters_max = cleaned_data.get("coordinate_uncertainty_in_meters_max")
		decimal_latitude_min = cleaned_data.get("decimal_latitude_min")
		decimal_latitude_max = cleaned_data.get("decimal_latitude_max")
		decimal_longitude_min = cleaned_data.get("decimal_longitude_min")
		decimal_longitude_max = cleaned_data.get("decimal_longitude_max")

		if coordinate_uncertainty_in_meters_min and coordinate_uncertainty_in_meters_max and coordinate_uncertainty_in_meters_min > coordinate_uncertainty_in_meters_max:
			raise forms.ValidationError("Minimum coordinate uncertainty cannot be greater than maximum coordinate uncertainty.")

		if decimal_latitude_min and decimal_latitude_max and decimal_latitude_min > decimal_latitude_max:
			raise forms.ValidationError("Minimum latitude cannot be greater than maximum latitude.")
		if decimal_longitude_min and decimal_longitude_max and decimal_longitude_min > decimal_longitude_max:
			raise forms.ValidationError("Minimum longitude cannot be greater than maximum longitude.")

		# print(f'---- CLEANED DATA \n\n {cleaned_data} \n\n----')

		return cleaned_data


class DateOccurrenceForm(CamelCaseForm):
	year_min = forms.IntegerField(required=False, label="Minimum Year")
	year_max = forms.IntegerField(required=False, label="Maximum Year")
	month_min = forms.IntegerField(required=False, label="Minimum Month")
	month_max = forms.IntegerField(required=False, label="Maximum Month")

	def clean(self):
		cleaned_data = super().clean()

		cleaned_data["collection_date_year_min"] = cleaned_data.pop("year_min", None)
		cleaned_data["collection_date_year_max"] = cleaned_data.pop("year_max", None)
		cleaned_data["collection_date_month_min"] = cleaned_data.pop("month_min", None)
		cleaned_data["collection_date_month_max"] = cleaned_data.pop("month_max", None)

		year_min = cleaned_data.get("collection_date_year_min")
		year_max = cleaned_data.get("collection_date_year_max")
		month_min = cleaned_data.get("collection_date_month_min")
		month_max = cleaned_data.get("collection_date_month_max")

		if year_min and year_max and year_min > year_max:
			raise forms.ValidationError("Minimum Year cannot be greater than Maximum Year.")

		if month_min and month_max and month_min > month_max:
			raise forms.ValidationError("Minimum Month cannot be greater than Maximum Month.")

		return cleaned_data


class OccurrenceForm(LatLonModelForm, DateOccurrenceForm):
	taxonomy = forms.IntegerField(required=False)
	voucher = forms.IntegerField(required=False)
	geographical_location = forms.IntegerField(required=False)
	collection_date_year = forms.IntegerField(required=False)
	collection_date_month = forms.IntegerField(required=False)
	collection_date_day = forms.IntegerField(required=False)
	basis_of_record = forms.IntegerField(required=False)
	batch = forms.IntegerField(required=False)
	sources = forms.IntegerField(required=False)
	add_synonyms = forms.BooleanField(required=False, initial=True)
	source = forms.CharField(required=False)
	has_sequence = forms.NullBooleanField(required=False, initial=None)

	TRANSLATE_FIELDS = {
		"year": "collection_date_year",
		"month": "collection_date_month",
		"day": "collection_date_day",
	}
