from django.urls import reverse
from rest_framework import status

from common.utils.tests import TestResultHandler

EXPECTED_MARKER = {
	"id": 1,
	"name": "Tyr",
	"unidecodeName": "Tyr",
	"accepted": True,
	"acceptedModifier": None,
	"product": "tyrosinase",
	"batch": 3,
	"sources": [136],
	"synonyms": [],
}

EXPECTED_SEQUENCE = {
	"id": 14,
	"isolate": "CAP01",
	"bp": 814,
	"definition": "Alytes muletensis isolate CAP01 NADH dehydrogenase subunit 4 (ND4) gene, partial cds; tRNA-His gene, complete sequence; and tRNA-Ser gene, partial sequence; mitochondrial",
	"dataFileDivision": "VRT",
	"publishedDate": None,
	"moleculeType": "DNA",
	"sequenceVersion": 1,
	"batch": 3,
	"occurrence": 114,
	"sources": [152],
	"markers": [5],
}


class SequenceCRUDTest(TestResultHandler):
	def test_sequence_crud_200(self):
		marker_id = 14
		url = reverse("genetics:sequence_crud") + f"?id={marker_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, EXPECTED_SEQUENCE)

	def test_sequence_crud_400(self):
		url = reverse("genetics:sequence_crud")
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_sequence_crud_404(self):
		marker_id = 9999
		url = reverse("genetics:sequence_crud") + f"?id={marker_id}"
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class SequenceSearchTest(TestResultHandler):
	def test_sequence_search_200(self):
		seq_def = "CAP01 NADH dehydrogenase subunit 4"
		url = reverse("genetics:sequence_search") + f"?definition={seq_def}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, [EXPECTED_SEQUENCE])

	def test_sequence_search_400(self):
		url = reverse("genetics:sequence_search")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class MarkerCRUDTest(TestResultHandler):
	def test_marker_crud_200(self):
		marker_id = 1
		url = reverse("genetics:marker_crud") + f"?id={marker_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, EXPECTED_MARKER)

	def test_marker_crud_400(self):
		url = reverse("genetics:marker_crud")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_marker_crud_404(self):
		invalid_marker_id = 9999
		url = reverse("genetics:marker_crud") + f"?id={invalid_marker_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class MarkerSearchTest(TestResultHandler):
	def test_marker_search_200(self):
		marker_name = "yr"
		url = reverse("genetics:marker_search") + f"?name={marker_name}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, [EXPECTED_MARKER])

	def test_marker_search_400(self):
		url = reverse("genetics:marker_search")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class MarkersListTest(TestResultHandler):
	def test_marker_list_200(self):
		taxon_id = 14
		url = reverse("genetics:marker_list") + f"?taxonomy={taxon_id}"
		response = self.client.get(url)
		expected_data = []
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_marker_list_400(self):
		url = reverse("genetics:marker_list")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_marker_list_404(self):
		invalid_taxonomy_id = 99999
		url = reverse("genetics:marker_list") + f"?taxonomy={invalid_taxonomy_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)
