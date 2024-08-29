from rest_framework import status
from rest_framework.reverse import reverse

from common.utils.tests import TestResultHandler


class TaxonSearchTest(TestResultHandler):
	def test_taxon_search_200(self):
		name = "animalia"
		url = reverse("taxonomy:search") + f"?name={name}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{
				"id": 2,
				"name": "Animalia",
				"taxonRank": "kingdom",
				"scientificNameAuthorship": None,
				"accepted": True,
				"acceptedModifier": "",
			}
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_search_400(self):
		url = reverse("taxonomy:search")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class TaxonListTest(TestResultHandler):
	def test_taxon_list_200(self):
		taxon_rank = "order"
		accepted = "true"
		url = reverse("taxonomy:list") + f"?taxonRank={taxon_rank}&accepted={accepted}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{
				"id": 5,
				"name": "Anura",
				"taxonRank": "order",
				"scientificNameAuthorship": None,
				"accepted": True,
				"acceptedModifier": "",
				"images": [],
				"parent": 4,
			}
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_list_400(self):
		taxon_rank = 4
		url = reverse("taxonomy:list") + f"?taxonRank={taxon_rank}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_list_404(self):
		taxon_rank = "family"
		accepted = "true"
		name = "animals"
		url = reverse("taxonomy:list") + f"?taxonRank={taxon_rank}&accepted={accepted}&name={name}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonCountTest(TestResultHandler):
	def test_taxon_list_count_200(self):
		taxon_rank = "order"
		accepted = "true"
		url = reverse("taxonomy:list_count") + f"?taxonRank={taxon_rank}&accepted={accepted}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = 1
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_list_count_400(self):
		taxon_rank = 4
		url = reverse("taxonomy:list_count") + f"?taxonRank={taxon_rank}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_list_count_404(self):
		taxon_rank = "family"
		accepted = "true"
		name = "animals"
		url = reverse("taxonomy:list_count") + f"?taxonRank={taxon_rank}&accepted={accepted}&name={name}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonCRUDTest(TestResultHandler):
	def test_taxon_crud_200(self):
		taxon_id = 2
		url = reverse("taxonomy:taxon_crud") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = {
			"id": 2,
			"name": "Animalia",
			"taxonRank": "kingdom",
			"scientificNameAuthorship": None,
			"accepted": True,
			"acceptedModifier": "",
			"images": [],
			"parent": 1,
		}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_crud_400(self):
		taxon_id = "dos"
		url = reverse("taxonomy:taxon_crud") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_crud_404(self):
		taxon_id = 99999
		url = reverse("taxonomy:taxon_crud") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonParentTest(TestResultHandler):
	def test_taxon_parent_200(self):
		url = reverse("taxonomy:taxon_parent") + "?id=3"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{
				"id": 1,
				"name": "Biota",
				"taxonRank": "life",
				"scientificNameAuthorship": None,
				"accepted": True,
				"acceptedModifier": "",
				"images": [],
				"parent": None,
			},
			{
				"id": 2,
				"name": "Animalia",
				"taxonRank": "kingdom",
				"scientificNameAuthorship": None,
				"accepted": True,
				"acceptedModifier": "",
				"images": [],
				"parent": 1,
			},
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_parent_400(self):
		url = reverse("taxonomy:taxon_parent")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_parent_404(self):
		url = reverse("taxonomy:taxon_parent") + "?id=99999"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonChildrenTest(TestResultHandler):
	def test_taxon_children_200(self):
		url = reverse("taxonomy:taxon_children") + "?id=3"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{
				"id": 4,
				"name": "Amphibia",
				"taxonRank": "class",
				"scientificNameAuthorship": None,
				"accepted": True,
				"acceptedModifier": "",
				"images": [],
				"parent": 3,
			}
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_children_400(self):
		url = reverse("taxonomy:taxon_children")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_children_404(self):
		url = reverse("taxonomy:taxon_children") + "?id=99999"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonChildrenCountTest(TestResultHandler):
	def test_taxon_children_count_200(self):
		url = reverse("taxonomy:taxon_children_count") + "?id=1"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_count = 1
		self.assert_and_log(self.assertEqual, response.json(), expected_count)

	def test_taxon_children_count_400(self):
		url = reverse("taxonomy:taxon_children_count")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_children_count_404(self):
		url = reverse("taxonomy:taxon_children_count") + "?id=99999"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonCompositionTest(TestResultHandler):
	def test_taxon_composition_200(self):
		taxon_id = 5
		url = reverse("taxonomy:taxon_composition") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{"id": 7, "name": "Bufonidae", "rank": 4, "totalSpecies": 2},
			{"id": 8, "name": "Hylidae", "rank": 4, "totalSpecies": 1},
			{"id": 9, "name": "Ranidae", "rank": 4, "totalSpecies": 1},
			{"id": 6, "name": "Alytidae", "rank": 4, "totalSpecies": 1},
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_composition_400(self):
		url = reverse("taxonomy:taxon_composition")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_composition_404(self):
		taxon_id = 99999
		url = reverse("taxonomy:taxon_composition") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonSynonymTest(TestResultHandler):
	def test_taxon_synonym_200(self):
		taxon_id = 14
		url = reverse("taxonomy:taxon_synonyms") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = []
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_synonym_400(self):
		url = reverse("taxonomy:taxon_synonyms")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_synonym_404(self):
		taxon_id = 99999
		url = reverse("taxonomy:taxon_synonyms") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonSourceTest(TestResultHandler):
	def test_taxon_source_200(self):
		taxon_id = 2
		url = reverse("taxonomy:taxon_sources") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{
				"id": 1,
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
				"originId": "N",
				"attribution": None,
			},
			{
				"id": 18,
				"source": {
					"id": 2,
					"name": "GBIF",
					"unidecodeName": "GBIF",
					"accepted": True,
					"acceptedModifier": None,
					"origin": 0,
					"url": None,
					"dataType": 0,
					"batch": None,
					"synonyms": [],
				},
				"originId": "1",
				"attribution": None,
			},
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_source_400(self):
		url = reverse("taxonomy:taxon_sources")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_source_404(self):
		taxon_id = 99999
		url = reverse("taxonomy:taxon_sources") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonChecklistTest(TestResultHandler):
	def test_taxon_checklist_200(self):
		taxon_id = 1
		url = reverse("taxonomy:taxon_checklist") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		self.assert_and_log(self.assertEqual, response["Content-Type"], "text/csv")

	def test_taxon_checklist_400(self):
		url = reverse("taxonomy:taxon_checklist")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_checklist_404(self):
		taxon_id = 99999
		url = reverse("taxonomy:taxon_checklist") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonDataCRUDTest(TestResultHandler):
	def test_taxon_data_crud_200(self):
		taxon_id = 14
		url = reverse("taxonomy:data_crud") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = {
			"id": 1,
			"iucnGlobal": "en",
			"iucnEurope": "en",
			"iucnMediterranean": "ne",
			"habitat": [
				{
					"sources": [
						{
							"id": 257,
							"source": {
								"id": 7,
								"name": "IUCN",
								"unidecodeName": "IUCN",
								"accepted": True,
								"acceptedModifier": None,
								"origin": 0,
								"url": None,
								"dataType": 0,
								"batch": None,
								"synonyms": [],
							},
							"originId": "5",
							"attribution": None,
						}
					],
					"name": "wetlands (inland)",
				},
				{
					"sources": [
						{
							"id": 266,
							"source": {
								"id": 7,
								"name": "IUCN",
								"unidecodeName": "IUCN",
								"accepted": True,
								"acceptedModifier": None,
								"origin": 0,
								"url": None,
								"dataType": 0,
								"batch": None,
								"synonyms": [],
							},
							"originId": "14",
							"attribution": None,
						}
					],
					"name": "artificial/terrestrial",
				},
				{
					"sources": [
						{
							"id": 267,
							"source": {
								"id": 7,
								"name": "IUCN",
								"unidecodeName": "IUCN",
								"accepted": True,
								"acceptedModifier": None,
								"origin": 0,
								"url": None,
								"dataType": 0,
								"batch": None,
								"synonyms": [],
							},
							"originId": "15",
							"attribution": None,
						}
					],
					"name": "artificial/aquatic",
				},
			],
			"invasive": False,
			"domesticated": False,
			"freshwater": True,
			"marine": False,
			"terrestrial": True,
		}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_data_crud_400(self):
		url = reverse("taxonomy:data_crud")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_data_crud_404(self):
		taxon_id = 99999
		url = reverse("taxonomy:data_crud") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


class TaxonDataListTest(TestResultHandler):
	def test_taxon_data_list_200(self):
		iucn_europe = "en"
		url = reverse("taxonomy:data_list") + f"?iucnEurope={iucn_europe}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{
				"id": 1,
				"iucnGlobal": "en",
				"iucnEurope": "en",
				"iucnMediterranean": "ne",
				"habitat": [
					{
						"sources": [
							{
								"id": 257,
								"source": {
									"id": 7,
									"name": "IUCN",
									"unidecodeName": "IUCN",
									"accepted": True,
									"acceptedModifier": None,
									"origin": 0,
									"url": None,
									"dataType": 0,
									"batch": None,
									"synonyms": [],
								},
								"originId": "5",
								"attribution": None,
							}
						],
						"name": "wetlands (inland)",
					},
					{
						"sources": [
							{
								"id": 266,
								"source": {
									"id": 7,
									"name": "IUCN",
									"unidecodeName": "IUCN",
									"accepted": True,
									"acceptedModifier": None,
									"origin": 0,
									"url": None,
									"dataType": 0,
									"batch": None,
									"synonyms": [],
								},
								"originId": "14",
								"attribution": None,
							}
						],
						"name": "artificial/terrestrial",
					},
					{
						"sources": [
							{
								"id": 267,
								"source": {
									"id": 7,
									"name": "IUCN",
									"unidecodeName": "IUCN",
									"accepted": True,
									"acceptedModifier": None,
									"origin": 0,
									"url": None,
									"dataType": 0,
									"batch": None,
									"synonyms": [],
								},
								"originId": "15",
								"attribution": None,
							}
						],
						"name": "artificial/aquatic",
					},
				],
				"invasive": False,
				"domesticated": False,
				"freshwater": True,
				"marine": False,
				"terrestrial": True,
			}
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_data_list_400(self):
		iucn_europe = "invalid"
		url = reverse("taxonomy:data_list") + f"?iucnEurope={iucn_europe}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class TaxonDataCountTest(TestResultHandler):
	def test_taxon_data_list_count_200(self):
		iucn_europe = "en"
		url = reverse("taxonomy:data_count") + f"?iucnEurope={iucn_europe}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = 1
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_data_list_count_400(self):
		iucn_europe = "invalid"
		url = reverse("taxonomy:data_count") + f"?iucnEurope={iucn_europe}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthorshipCRUDTest(TestResultHandler):
	def test_authorship_crud_200(self):
		taxon_id = 1
		url = reverse("taxonomy:authorship_crud") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = {"id": 1, "name": "Fitzinger", "accepted": True}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_authorship_crud_400(self):
		url = reverse("taxonomy:authorship_crud")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_authorship_crud_404(self):
		taxon_id = 99999
		url = reverse("taxonomy:authorship_crud") + f"?id={taxon_id}"
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)
