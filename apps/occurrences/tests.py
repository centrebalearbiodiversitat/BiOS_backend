from django.urls import reverse
from rest_framework import status

from common.utils.tests import TestResultHandler

EXPECTED_OCURRENCE = {
	"id": 1,
	"basisOfRecord": 4,
	"coordinateUncertaintyInMeters": 28030,
	"decimalLatitude": 39.99735,
	"decimalLongitude": 2.82283,
	"depth": None,
	"elevation": None,
	"location": 1,
	"taxonomy": 14,
}

class OccurrenceCRUDTest(TestResultHandler):
	def test_occurrence_crud_200(self):
		occurrence_id = 1
		url = reverse("occurrences:occurrence_crud") + f"?id={occurrence_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, EXPECTED_OCURRENCE)

	def test_occurrence_crud_400(self):
		url = reverse("occurrences:occurrence_crud")
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		expected_data = {"detail": "Missing id parameter"}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_occurrence_crud_404(self):
		invalid_occurrence_id = 99999
		url = reverse("occurrences:occurrence_crud") + f"?id={invalid_occurrence_id}"
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		expected_data = {"detail": "Occurrence does not exist"}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)


class OccurrenceListTest(TestResultHandler):
	def test_occurrence_list_200(self):
		taxonomy_id = 14
		decimal_latitude_min = 39.99
		decimal_latitude_max = 40
		coordinate_uncertainty_in_meters_min = 28000
		url = reverse("occurrences:occurrence_list")+ f"?taxonomy={taxonomy_id}&decimalLatitudeMin={decimal_latitude_min}&decimalLatitudeMax={decimal_latitude_max}&coordinateUncertaintyInMetersMin={coordinate_uncertainty_in_meters_min}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, [EXPECTED_OCURRENCE])

	def test_occurrence_list_400(self):
		url = reverse("occurrences:occurrence_list") + "?taxonomy=invalid"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_occurrence_list_404(self):
		url = reverse("occurrences:occurrence_list") + "?taxonomy=9999"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class OccurrenceCountTest(TestResultHandler):
	def test_occurrence_count_200(self):
		taxon_id = 14
		url = reverse("occurrences:occurrence_list_count") + f"?taxonomy={taxon_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = 164
		self.assert_and_log(self.assertEqual, response.data, expected_data)

	def test_occurrence_count_400(self):
		url = reverse("occurrences:occurrence_list_count") + "?taxonomy=none"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_occurrence_count_404(self):
		taxon_id = 99999
		url = reverse("occurrences:occurrence_list_count") + f"taxonomy={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)
