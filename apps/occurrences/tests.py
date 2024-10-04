from rest_framework import status

from common.utils.tests import TestResultHandler

EXPECTED_OCURRENCE = [
    {
        "id": 26
    },
    {
        "id": 95
    },
    {
        "id": 58
    },
    {
        "id": 49
    },
    {
        "id": 54
    },
    {
        "id": 52
    },
    {
        "id": 57
    },
    {
        "id": 56
    },
    {
        "id": 51
    },
    {
        "id": 53
    },
    {
        "id": 50
    },
    {
        "id": 55
    },
    {
        "id": 94
    }
]
class OccurrencesTest(TestResultHandler):
	def test_occurrence_crud_200(self):
		occurrence_id = 1
		choice = "id,coordinateUncertaintyInMeters,taxonomy"
		url = self._generate_url("occurrences:occurrence_crud", id=occurrence_id, choice=choice)
		response = self.client.get(url)
		expected_data = {
			"id": 1,
			"coordinateUncertaintyInMeters": 1000,
			"taxonomy": {
				"id": 14,
				"name": "Alytes muletensis",
				"taxonRank": "species",
				"scientificNameAuthorship": "(Sanchíz & Adrover, 1979)",
				"accepted": True,
				"acceptedModifier": "",
				"images": [],
				"parent": 10
			}
		}
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_occurrence_crud_400(self):
		url = self._generate_url("occurrences:occurrence_crud")
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		expected_data = {"detail": "Missing id parameter"}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_occurrence_crud_404(self):
		invalid_occurrence_id = 99999
		url = self._generate_url("occurrences:occurrence_crud", id=invalid_occurrence_id)
		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		expected_data = {"detail": "Occurrence does not exist"}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)
	
	def test_occurrence_list_200(self):
		taxonomy_id = 14
		coordinate_uncertainty_in_meters_max = 100
		choice = "id"
		url = self._generate_url(
			"occurrences:occurrence_list",
			taxonomy=taxonomy_id,
			coordinateUncertaintyInMetersMax=coordinate_uncertainty_in_meters_max,
			choice=choice
		)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, EXPECTED_OCURRENCE)

	def test_occurrence_list_400(self):
		url = self._generate_url("occurrences:occurrence_list", taxonomy="invalid")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_occurrence_list_404(self):
		url = self._generate_url("occurrences:occurrence_list", taxonomy=9999)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_occurrence_count_200(self):
		taxon_id = 14
		url = self._generate_url("occurrences:occurrence_list_count", taxonomy=taxon_id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = 104
		self.assert_and_log(self.assertEqual, response.data, expected_data)

	def test_occurrence_count_400(self):
		url = self._generate_url("occurrences:occurrence_list_count", taxonomy=None)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_occurrence_count_404(self):
		taxon_id = 99999
		url = self._generate_url("occurrences:occurrence_list_count", taxonomy=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_occurrence_count_by_source_200(self):
		taxonomy = 14
		url = self._generate_url("occurrences:occurrence_source_stats", taxonomy=taxonomy)
		response = self.client.get(url)
		expected_data = [
			{
			"source": "GBIF",
			"count": 104
		}
		]
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertEqual, response.data, expected_data)

	def test_occurrence_count_by_source_400(self):
		url = self._generate_url("occurrences:occurrence_source_stats")
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_occurrence_count_by_taxon_and_children_200(self):
		taxonomy= 5
		url = self._generate_url("occurrences:occurrence_children_stats", taxonomy=taxonomy)
		response = self.client.get(url)
		expected_data = [
			{
				"taxonomy": "Alytidae",
				"count": 104
			}
		]
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_occurrence_count_by_taxon_and_children_400(self):
		taxonomy= None
		url = self._generate_url("occurrences:occurrence_children_stats", taxonomy=taxonomy)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_occurrence_count_by_taxon_and_children_404(self):
		url = self._generate_url("occurrences:occurrence_children_stats", taxonomy=9999)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_occurrence_month_stats_200(self):
		taxonomy= 14
		url = self._generate_url("occurrences:occurrence_month_stats", taxonomy=taxonomy)
		response = self.client.get(url)
		expected_data = [
			{
				"count": 8,
				"month": 1
			},
			{
				"count": 2,
				"month": 3
			},
			{
				"count": 16,
				"month": 4
			},
			{
				"count": 15,
				"month": 5
			},
			{
				"count": 12,
				"month": 6
			},
			{
				"count": 15,
				"month": 7
			},
			{
				"count": 4,
				"month": 8
			},
			{
				"count": 2,
				"month": 9
			},
			{
				"count": 8,
				"month": 12
			},
			{
				"count": 22,
				"month": None
			}
		]
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_occurrence_month_stats_400(self):
		taxonomy= None
		url = self._generate_url("occurrences:occurrence_month_stats", taxonomy=taxonomy)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_occurrence_month_stats_404(self):
		url = self._generate_url("occurrences:occurrence_month_stats", taxonomy=9999)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_occurrence_year_stats_200(self):
		taxonomy= 14
		url = self._generate_url("occurrences:occurrence_year_stats", taxonomy=taxonomy)
		response = self.client.get(url)
		expected_data = [
			{
				"count": 2,
				"source": 1971
			},
			{
				"count": 2,
				"source": 1982
			},
			{
				"count": 1,
				"source": 1985
			},
			{
				"count": 2,
				"source": 1986
			},
			{
				"count": 1,
				"source": 1991
			},
			{
				"count": 8,
				"source": 2006
			},
			{
				"count": 3,
				"source": 2008
			},
			{
				"count": 1,
				"source": 2010
			},
			{
				"count": 4,
				"source": 2012
			},
			{
				"count": 2,
				"source": 2013
			},
			{
				"count": 3,
				"source": 2014
			},
			{
				"count": 2,
				"source": 2015
			},
			{
				"count": 1,
				"source": 2017
			},
			{
				"count": 5,
				"source": 2018
			},
			{
				"count": 20,
				"source": 2019
			},
			{
				"count": 12,
				"source": 2021
			},
			{
				"count": 21,
				"source": 2022
			},
			{
				"count": 1,
				"source": 2023
			},
			{
				"count": 4,
				"source": 2024
			},
			{
				"count": 9,
				"source": None
			}
		]
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_occurrence_year_stats_400(self):
		taxonomy= None
		url = self._generate_url("occurrences:occurrence_year_stats", taxonomy=taxonomy)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_occurrence_year_stats_404(self):
		url = self._generate_url("occurrences:occurrence_year_stats", taxonomy=9999)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)