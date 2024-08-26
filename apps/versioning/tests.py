from django.urls import reverse
from rest_framework import status

from common.utils.tests import TestResultHandler

class SourceSearchTest(TestResultHandler):

	def test_source_search_200(self):
		source_name = "gb"
		url = reverse("versioning:source_search") + f"?name={source_name}"
		response = self.client.get(url)
		expected_data = [
			{
				"id": 2,
				"name": "GBIF",
				"unidecodeName": "GBIF",
				"accepted": True,
				"acceptedModifier": None,
				"origin": 0,
				"url": None,
				"dataType": 0,
				"batch": None,
				"synonyms": []
			},
			{
				"id": 3,
				"name": "GBIF",
				"unidecodeName": "GBIF",
				"accepted": True,
				"acceptedModifier": None,
				"origin": 0,
				"url": None,
				"dataType": 1,
				"batch": None,
				"synonyms": []
			}
		]
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_source_search_400(self):
		url = reverse("versioning:source_search")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class SourceCRUDTest(TestResultHandler):

	def test_source_crud_200(self):
		source_id = 3
		url = reverse("versioning:source_crud") + f"?id={source_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = {
			"id": 3,
			"name": "GBIF",
			"unidecodeName": "GBIF",
			"accepted": True,
			"acceptedModifier": None,
			"origin": 0,
			"url": None,
			"dataType": 1,
			"batch": None,
			"synonyms": [],
		}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_source_crud_400(self):
		url = reverse("versioning:source_crud")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_source_crud_404(self):
		source_id = 9999
		url = reverse("versioning:source_crud") + f"?id={source_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class SourceListTest(TestResultHandler):

	def test_source_list_200(self):
		name = "NCBI"
		origin = "database"
		accepted = "True"
		url = reverse("versioning:source_list") + f"?name={name}&origin={origin}&accepted={accepted}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = [
			{
				"id": 4,
				"name": "NCBI",
				"unidecodeName": "NCBI",
				"accepted": True,
				"acceptedModifier": None,
				"origin": 0,
				"url": None,
				"dataType": 0,
				"batch": None,
				"synonyms": [],
			},
			{
				"id": 5,
				"name": "NCBI",
				"unidecodeName": "NCBI",
				"accepted": True,
				"acceptedModifier": None,
				"origin": 0,
				"url": None,
				"dataType": 1,
				"batch": None,
				"synonyms": [],
			},
			{
				"id": 6,
				"name": "NCBI",
				"unidecodeName": "NCBI",
				"accepted": True,
				"acceptedModifier": None,
				"origin": 0,
				"url": None,
				"dataType": 2,
				"batch": None,
				"synonyms": [],
			},
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_source_list_400(self):
		origin = 0
		url = reverse("versioning:source_list") + f"?origin={origin}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_source_list_404(self):
		url = reverse("versioning:source_list")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class OriginSourceCRUDTest(TestResultHandler):

	def test_origin_source_crud_200(self):
		os_id = 2
		url = reverse("versioning:os_crud") + f"?id={os_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = {
			"id": 2,
			"source": {
				"id": 1,
				"name": "Catalogue of Life",
				"unidecodeName": "Catalogue of Life",
				"accepted": True,
				"acceptedModifier": None,
				"origin": 0,
				"url": None,
				"dataType": 0,
				"batch": None,
				"synonyms": [],
			},
			"originId": "CH2",
			"attribution": None,
		}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_origin_source_crud_400(self):
		url = reverse("versioning:os_crud")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_origin_source_crud_404(self):
		os_id = 9999
		url = reverse("versioning:os_crud") + f"?id={os_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)
