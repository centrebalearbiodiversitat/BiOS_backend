from rest_framework import status

from common.utils.tests import TestResultHandler


class TaxonomyTest(TestResultHandler):
	def test_taxon_search_200(self):
		name = "animalia"
		url = self._generate_url("taxonomy:search", name=name)
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
		url = self._generate_url("taxonomy:search")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_list_200(self):
		taxon_rank = "order"
		accepted = "true"
		url = self._generate_url("taxonomy:list", taxonRank=taxon_rank, accepted=accepted)
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
		url = self._generate_url("taxonomy:list", taxonRank=taxon_rank)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_list_404(self):
		taxon_rank = "family"
		accepted = "true"
		name = "animals"
		url = self._generate_url("taxonomy:list", taxonRank=taxon_rank, accepted=accepted, name=name)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_list_count_200(self):
		taxon_rank = "order"
		accepted = "true"
		url = self._generate_url("taxonomy:list_count", taxonRank=taxon_rank, accepted=accepted)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = 1
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_list_count_400(self):
		taxon_rank = 4
		url = self._generate_url("taxonomy:list_count", taxonRank=taxon_rank)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_list_count_404(self):
		taxon_rank = "family"
		accepted = "true"
		name = "animals"
		url = self._generate_url("taxonomy:list_count", taxonRank=taxon_rank, accepted=accepted, name=name)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_crud_200(self):
		taxon_id = 2
		url = self._generate_url("taxonomy:taxon_crud", id=taxon_id)
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
		url = self._generate_url("taxonomy:taxon_crud", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_crud_404(self):
		taxon_id = 99999
		url = self._generate_url("taxonomy:taxon_crud", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_parent_200(self):
		url = self._generate_url("taxonomy:taxon_parent", id=3)
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
		url = self._generate_url("taxonomy:taxon_parent")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_parent_404(self):
		url = self._generate_url("taxonomy:taxon_parent", id=99999)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_children_200(self):
		url = self._generate_url("taxonomy:taxon_children", id=3)
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
		url = self._generate_url("taxonomy:taxon_children")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_children_404(self):
		url = self._generate_url("taxonomy:taxon_children", id=99999)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_children_count_200(self):
		url = self._generate_url("taxonomy:taxon_children_count", id=1)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_count = 1
		self.assert_and_log(self.assertEqual, response.json(), expected_count)

	def test_taxon_children_count_400(self):
		url = self._generate_url("taxonomy:taxon_children_count")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_children_count_404(self):
		url = self._generate_url("taxonomy:taxon_children_count", id=99999)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_descendants_count_200(self):
		url = self._generate_url("taxonomy:taxon_descendants_count", id=5)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = {"family": 4, "genus": 4, "species": 5}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_descendants_count_400(self):
		url = self._generate_url("taxonomy:taxon_descendants_count", id=None)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_descendants_count_404(self):
		url = self._generate_url("taxonomy:taxon_descendants_count", id=99999)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_synonym_200(self):
		taxon_id = 14
		url = self._generate_url("taxonomy:taxon_synonyms", id=taxon_id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = []
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_synonym_400(self):
		url = self._generate_url("taxonomy:taxon_synonyms")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_synonym_404(self):
		taxon_id = 99999
		url = self._generate_url("taxonomy:taxon_synonyms", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_composition_200(self):
		taxon_id = 5
		url = self._generate_url("taxonomy:taxon_composition", id=taxon_id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{"id": 6, "name": "Alytidae", "rank": 4, "totalSpecies": 1},
			{"id": 7, "name": "Bufonidae", "rank": 4, "totalSpecies": 2},
			{"id": 8, "name": "Hylidae", "rank": 4, "totalSpecies": 1},
			{"id": 9, "name": "Ranidae", "rank": 4, "totalSpecies": 1},
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_composition_400(self):
		url = self._generate_url("taxonomy:taxon_composition")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_composition_404(self):
		taxon_id = 99999
		url = self._generate_url("taxonomy:taxon_composition", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_source_200(self):
		taxon_id = 2
		exclude = "id"
		url = self._generate_url("taxonomy:taxon_sources", id=taxon_id, exclude=exclude)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{
				"source": {
					"name": "Catalogue of Life",
					"url": None,
					"origin": "database",
					"dataType": "taxon"
				},
				"originId": "N",
				"attribution": None
			},
			{
				"source": {
					"name": "GBIF",
					"url": None,
					"origin": "database",
					"dataType": "taxon"
				},
				"originId": "1",
				"attribution": None
			}
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_source_400(self):
		url = self._generate_url("taxonomy:taxon_sources")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_source_404(self):
		taxon_id = 99999
		url = self._generate_url("taxonomy:taxon_sources", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_checklist_200(self):
		taxon_id = 1
		url = self._generate_url("taxonomy:taxon_checklist", id=taxon_id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		self.assert_and_log(self.assertEqual, response["Content-Type"], "text/csv")

	def test_taxon_checklist_400(self):
		url = self._generate_url("taxonomy:taxon_checklist")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_checklist_404(self):
		taxon_id = 99999
		url = self._generate_url("taxonomy:taxon_checklist", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_data_crud_200(self):
		taxonomy = 14
		exclude = "id"

		url = self._generate_url("taxonomy:data_crud", taxonomy=taxonomy, exclude=exclude)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = {
			"iucnGlobal": "en",
			"iucnEurope": "en",
			"iucnMediterranean": "ne",
			"habitat": [
				{
					"sources": [
						{
							"source": {
								"name": "IUCN",
								"url": None,
								"origin": "database",
								"dataType": "taxon"
							},
							"originId": "5",
							"attribution": None
						}
					],
					"name": "wetlands (inland)"
				},
				{
					"sources": [
						{
							"source": {
								"name": "IUCN",
								"url": None,
								"origin": "database",
								"dataType": "taxon"
							},
							"originId": "14",
							"attribution": None
						}
					],
					"name": "artificial/terrestrial"
				},
				{
					"sources": [
						{
							"source": {
								"name": "IUCN",
								"url": None,
								"origin": "database",
								"dataType": "taxon"
							},
							"originId": "15",
							"attribution": None
						}
					],
					"name": "artificial/aquatic"
				}
			],
			"tags": [
				{
					"name": "endemic",
					"tagType": "ecological"
				},
				{
					"name": "wild",
					"tagType": "ecological"
				}
			],
			"freshwater": True,
			"marine": False,
			"terrestrial": True
		}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_data_crud_400(self):
		url = self._generate_url("taxonomy:data_crud")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_data_crud_404(self):
		taxon_id = 99999
		url = self._generate_url("taxonomy:data_crud", taxonomy=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)

	def test_taxon_data_list_200(self):
		taxonomy = 14
		exclude = "id"
		url = self._generate_url("taxonomy:data_list", taxonomy=taxonomy, exclude=exclude)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = [
			{
				"iucnGlobal": "en",
				"iucnEurope": "en",
				"iucnMediterranean": "ne",
				"habitat": [
					{
						"sources": [
							{
								"source": {
									"name": "IUCN",
									"url": None,
									"origin": "database",
									"dataType": "taxon"
								},
								"originId": "5",
								"attribution": None
							}
						],
						"name": "wetlands (inland)"
					},
					{
						"sources": [
							{
								"source": {
									"name": "IUCN",
									"url": None,
									"origin": "database",
									"dataType": "taxon"
								},
								"originId": "14",
								"attribution": None
							}
						],
						"name": "artificial/terrestrial"
					},
					{
						"sources": [
							{
								"source": {
									"name": "IUCN",
									"url": None,
									"origin": "database",
									"dataType": "taxon"
								},
								"originId": "15",
								"attribution": None
							}
						],
						"name": "artificial/aquatic"
					}
				],
				"tags": [
					{
						"name": "endemic",
						"tagType": "ecological"
					},
					{
						"name": "wild",
						"tagType": "ecological"
					}
				],
				"freshwater": True,
				"marine": False,
				"terrestrial": True
			}
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_data_list_400(self):
		iucn_europe = "invalid"
		url = self._generate_url("taxonomy:data_list", iucnEurope=iucn_europe)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_taxon_data_list_count_200(self):
		taxonomy = 14
		url = self._generate_url("taxonomy:data_count", taxonomy=taxonomy)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = 1
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_taxon_data_list_count_400(self):
		iucn_europe = "invalid"
		url = self._generate_url("taxonomy:data_count", iucnEurope=iucn_europe)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_data_habitats_200(self):
		url = self._generate_url("taxonomy:data_habitats", taxonomy=5)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = [
			{"name": "artificial/aquatic"},
			{"name": "artificial/terrestrial"},
			{"name": "desert"},
			{"name": "forest"},
			{"name": "grassland"},
			{"name": "marine coastal/supratidal"},
			{"name": "shrubland"},
			{"name": "wetlands (inland)"},
		]
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_data_habitats_400(self):
		url = self._generate_url("taxonomy:data_habitats", taxonomy=None)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_data_habitats_404(self):
		url = self._generate_url("taxonomy:data_habitats", taxonomy=99999)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
	
	def test_tag_crud_200(self):
		taxon_id = 1
		url = self._generate_url("taxonomy:tag_crud", id=taxon_id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		expected_data = {
			"name": "invasive",
			"tag_type": "ecological"
		}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_tag_crud_400(self):
		taxon_id = "dos"
		url = self._generate_url("taxonomy:tag_crud", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_tag_crud_404(self):
		taxon_id = 99999
		url = self._generate_url("taxonomy:tag_crud", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)


	def test_authorship_crud_200(self):
		taxon_id = 1
		url = self._generate_url("taxonomy:authorship_crud", id=taxon_id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		expected_data = {"id": 1, "name": "Fitzinger", "accepted": True}
		self.assert_and_log(self.assertJSONEqual, response.content, expected_data)

	def test_authorship_crud_400(self):
		url = self._generate_url("taxonomy:authorship_crud")
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_authorship_crud_404(self):
		taxon_id = 99999
		url = self._generate_url("taxonomy:authorship_crud", id=taxon_id)
		response = self.client.get(url)
		self.assert_and_log(self.assertEqual, response.status_code, status.HTTP_404_NOT_FOUND)
