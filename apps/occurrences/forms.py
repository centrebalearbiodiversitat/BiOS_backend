from apps.geography.models import GeographicLevel
from common.utils.forms import TranslateForm, IdFieldForm
from django import forms
from common.utils.forms import IdFieldForm, TranslateForm


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
		coordinate_uncertainty_in_meters_min = cleaned_data.get("coordinate_uncertainty_in_meters_min")
		coordinate_uncertainty_in_meters_max = cleaned_data.get("coordinate_uncertainty_in_meters_max")
		latitude_min = cleaned_data.get("latitude_min")
		latitude_max = cleaned_data.get("latitude_max")
		longitude_min = cleaned_data.get("longitude_min")
		longitude_max = cleaned_data.get("longitude_max")

		if (
			coordinate_uncertainty_in_meters_min
			and coordinate_uncertainty_in_meters_max
			and coordinate_uncertainty_in_meters_min > coordinate_uncertainty_in_meters_max
		):
			raise forms.ValidationError("Minimum coordinate uncertainty cannot be greater than maximum coordinate uncertainty.")
		if latitude_min and latitude_max and latitude_min > latitude_max:
			raise forms.ValidationError("Minimum latitude cannot be greater than maximum latitude.")

		if longitude_min and longitude_max and longitude_min > longitude_max:
			raise forms.ValidationError("Minimum longitude cannot be greater than maximum longitude.")

		return cleaned_data


class OccurrenceForm(LatLonModelForm):
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

	TRANSLATE_FIELDS = {
		"year": "collection_date_year",
		"month": "collection_date_month",
		"day": "collection_date_day",
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
