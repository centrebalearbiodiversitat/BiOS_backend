from django.urls import reverse
from rest_framework import status

from common.utils.tests import TestResultHandler

EXPECTED_GEO = {
	"id": 4,
	"parent": 1,
	"name": "Mallorca",
	"rank": "island",
	"decimalLatitude": 39.64434,
	"decimalLongitude": 2.89087,
	"coordinateUncertaintyInMeters": 57620,
	"elevation": None,
	"depth": None,
}


class GeographicLevelSearchTest(TestResultHandler):
	def test_geographic_level_search_200(self):
		name = "mallorca"
		exact = "true"
		url = reverse("geography:geo_search") + f"?name={name}&exact={exact}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, [EXPECTED_GEO])

	def test_geographic_level_search_400(self):
		url = reverse("geography:geo_search")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class GeographicLevelCRUDTest(TestResultHandler):
	def test_geographic_level_crud_200(self):
		geo_id = 4
		url = reverse("geography:geo_crud") + f"?id={geo_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, EXPECTED_GEO)

	def test_geographic_level_crud_400(self):
		url = reverse("geography:geo_crud")
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_geographic_level_crud_404(self):
		invalid_level_id = 9999
		url = reverse("geography:geo_crud") + f"?id={invalid_level_id}"
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class GeographicLevelListTest(TestResultHandler):
	def test_geographic_level_list_200(self):
		parent_id = 1
		rank = "island"
		name = "ma"
		url = reverse("geography:geo_list") + f"?parent={parent_id}&rank={rank}&name={name}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, [EXPECTED_GEO])

	def test_geographic_level_list_400(self):
		url = reverse("geography:geo_list") + "?rank=rango_invalido"
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class GeographicLevelCountTest(TestResultHandler):
	def test_geographic_level_list_count_200(self):
		parent_id = 1
		rank = "island"
		name = "ma"
		url = reverse("geography:geo_list_count") + f"?parent={parent_id}&rank={rank}&name={name}"
		response = self.client.get(url)
		expected_data = 1
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_geographic_level_list_count_400(self):
		rank = "invalid_rank"
		url = reverse("geography:geo_list_count") + f"?rank={rank}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class GeographicLevelParentTest(TestResultHandler):
	def test_geographic_level_parent_200(self):
		valid_level_id = 4
		url = reverse("geography:geo_level_parent") + f"?id={valid_level_id}"
		response = self.client.get(url)
		expected_data = [
			{
				"id": 1,
				"parent": None,
				"name": "Islas Baleares",
				"rank": "ac",
				"decimalLatitude": 39.37029,
				"decimalLongitude": 2.75802,
				"coordinateUncertaintyInMeters": 160840,
				"elevation": None,
				"depth": None,
			}
		]
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_geographic_level_parent_400(self):
		url = reverse("geography:geo_level_parent")
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_geographic_level_parent_404(self):
		invalid_level_id = 9999
		url = reverse("geography:geo_level_parent") + f"?id={invalid_level_id}"
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class GeographicLevelChildrenTest(TestResultHandler):
	def test_geographic_level_children_200(self):
		children_id = 3
		url = reverse("geography:geo_level_children") + f"?id={children_id}"
		response = self.client.get(url)
		expected_data = [
			{
				"id": 19,
				"parent": 3,
				"name": "Formentera",
				"rank": "municipality",
				"decimalLatitude": 38.70279,
				"decimalLongitude": 1.47943,
				"coordinateUncertaintyInMeters": 11017,
				"elevation": None,
				"depth": None,
			}
		]
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_geographic_level_children_400(self):
		children_id = None
		url = reverse("geography:geo_level_children") + f"?id={children_id}"
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_geographic_level_children_404(self):
		invalid_level_id = 9999
		url = reverse("geography:geo_level_children") + f"?id={invalid_level_id}"
		response = self.client.get(url)

		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)
