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

EXPECTED_LIST = [
	{"name": "ND5"},
	{"name": "COX3"},
	{"name": "COX1"},
	{"name": "ND2"},
	{"name": "RPL9"},
	{"name": "ND4"},
	{"name": "c-myc"},
	{"name": "Cytb"},
	{"name": "PPP3CA"},
	{"name": "ND6"},
	{"name": "ND3"},
	{"name": "ND4L"},
	{"name": "ATP6"},
	{"name": "COX2"},
	{"name": "ND1"},
	{"name": "Tyr"},
	{"name": "beta-fibrinogen"},
	{"name": "16S rRNA"},
	{"name": "12S rRNA"},
]


class GeneticsTest(TestResultHandler):
	def test_sequence_crud_200(self):
		marker_id = 14
		url = self._generate_url("genetics:sequence_crud", id=marker_id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, EXPECTED_SEQUENCE)

	def test_sequence_crud_400(self):
		url = self._generate_url("genetics:sequence_crud")
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_sequence_crud_404(self):
		marker_id = 9999
		url = self._generate_url("genetics:sequence_crud", id=marker_id)
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_sequence_search_200(self):
		seq_def = "CAP01 NADH dehydrogenase subunit 4"
		url = self._generate_url("genetics:sequence_search", definition=seq_def)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, [EXPECTED_SEQUENCE])

	def test_sequence_search_400(self):
		url = self._generate_url("genetics:sequence_search")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_marker_crud_200(self):
		marker_id = 1
		url = self._generate_url("genetics:marker_crud", id=marker_id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, EXPECTED_MARKER)

	def test_marker_crud_400(self):
		url = self._generate_url("genetics:marker_crud")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_marker_crud_404(self):
		invalid_marker_id = 9999
		url = self._generate_url("genetics:marker_crud", id=invalid_marker_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_marker_search_200(self):
		marker_name = "yr"
		url = self._generate_url("genetics:marker_search", name=marker_name)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, [EXPECTED_MARKER])

	def test_marker_search_400(self):
		url = self._generate_url("genetics:marker_search")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_marker_list_200(self):
		taxon_id = 14
		choice = "name"
		url = self._generate_url("genetics:marker_list", taxonomy=taxon_id, choice=choice)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, EXPECTED_LIST)

	def test_marker_list_400(self):
		url = self._generate_url("genetics:marker_list")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_marker_list_404(self):
		invalid_taxonomy_id = 99999
		url = self._generate_url("genetics:marker_list", taxonomy=invalid_taxonomy_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_marker_list_count_200(self):
		taxon_id = 14
		total = 4
		url = self._generate_url("genetics:marker_list_count", taxonomy=taxon_id, total=total)
		response = self.client.get(url)
		expected_data = 45
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_marker_list_count_400(self):
		url = self._generate_url("genetics:marker_list_count")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_marker_list_count_404(self):
		invalid_taxonomy_id = 99999
		url = self._generate_url("genetics:marker_list_count", taxonomy=invalid_taxonomy_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)
