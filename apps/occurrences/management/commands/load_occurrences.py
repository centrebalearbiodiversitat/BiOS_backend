import csv
import json

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.genetics.models import GeneticFeatures, Produces, Gene, Product
from apps.geography.models import GeographicLevel
from apps.occurrences.models import Occurrence
from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import Batch, Source, OriginSource

TAXON_KEYS = [
	("kingdom", "kingdomKey", TaxonomicLevel.KINGDOM),
	("phylum", "phylumKey", TaxonomicLevel.PHYLUM),
	("class", "classKey", TaxonomicLevel.CLASS),
	("order", "orderKey", TaxonomicLevel.ORDER),
	("family", "familyKey", TaxonomicLevel.FAMILY),
	("genus", "genusKey", TaxonomicLevel.GENUS),
	("specificEpithet", "speciesKey", TaxonomicLevel.SPECIES),
	# ("infraspecificEpithet", "subspeciesKey", TaxonomicLevel.SUBSPECIES),
	# ('varietyEpithet', 'varietyKey', TaxonomicLevel.VARIETY),
]

GEOGRAPHIC_LEVELS = [
	{"key": "AC", "rank": GeographicLevel.AC},
	{"key": "ISLAND", "rank": GeographicLevel.ISLAND},
	{"key": "MUNICIPALI", "rank": GeographicLevel.MUNICIPALITY},
	{"key": "TOWN", "rank": GeographicLevel.TOWN},
	{"key": "WB_0", "rank": GeographicLevel.WATER_BODY},
]


def parse_line(line: dict):
	for key, value in line.items():
		try:
			line[key] = json.loads(value)
		except:
			pass  # is not json format

	return line


def genetic_sources(line: dict, batch):
	gfs, _ = GeneticFeatures.objects.get_or_create(
		sample_id=line["sample_id"],
		defaults={
			"isolate": line["isolate"],
			"bp": line["bp"],
			"definition": line["definition"],
			"data_file_division": line["data_file_division"],
			"published_date": parse_datetime(line["date"]) if line["date"] else None,
			"collection_date": parse_datetime(line["collection_date"]) if line["collection_date"] else None,
			"molecule_type": line["molecule_type"],
			"sequence_version": line["sequence_version"],
		},
	)

	gfs.references.add(batch)

	for production in line["genetic_features"]:
		gene = None
		product = None
		if production["gene"]:
			gene, _ = Gene.objects.get_or_create(name=production["gene"], accepted=True)
			gene.references.add(batch)
		if production["product"]:
			product, _ = Product.objects.get_or_create(name=production["product"], accepted=True)
			product.references.add(batch)
		prod_rel, _ = Produces.objects.get_or_create(gene=gene, product=product)
		prod_rel.references.add(batch)
		gfs.products.add(prod_rel)


def find_gadm(line):
	gadm_query = ""
	for gl_key in GEOGRAPHIC_LEVELS:
		if line[gl_key["key"]]:
			gadm_query = f'{gadm_query}, {line[gl_key["key"]]}'

	return GeographicLevel.objects.search(location=gadm_query)


def create_origin_source(ref_model_elem, origin_id, source):
	os, new = OriginSource.objects.get_or_create(origin_id=origin_id, source=source)

	if new:
		ref_model_elem.sources.add(os)
	else:
		if not ref_model_elem.sources.filter(id=os.id).exists():
			raise Exception(
				f"Origin id already assigned to another model. {ref_model_elem}, {ref_model_elem.sources}, {os}"
			)


class Command(BaseCommand):
	help = "Loads occurrences from csv"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)
		parser.add_argument("-d", nargs="?", type=str, default=",")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		delimiter = options["d"]
		with open(file_name, encoding="utf-8") as file:
			csv_file = csv.DictReader(file, delimiter=delimiter)
			batch = Batch.objects.create()
			biota = TaxonomicLevel.objects.get(rank=TaxonomicLevel.LIFE)
			line: dict
			for line in csv_file:
				# print(line)
				line = parse_line(line)
				source, _ = Source.objects.get_or_create(
					name__icontains=line["occurrenceSource"],
					defaults={
						"name": line["occurrenceSource"],
						"accepted": True,
						"origin": Source.TRANSLATE_CHOICES[line["occurrenceOrigin"]],
					},
				)

				taxon = biota
				for taxon_key, taxon_id_key, taxon_rank in TAXON_KEYS:
					if line[taxon_key] and line[taxon_id_key]:
						taxon = taxon.get_descendants().filter(rank=taxon_rank, name__iexact=line[taxon_key])
						if taxon.count() > 1:
							raise Exception(f"Found multiple taxa for {taxon_key}:{taxon_id_key}.\n{line}")
						elif taxon.count() == 0:
							continue

						taxon = taxon.first()

						# if not taxon.sources.all().filter(origin_id=line[taxon_id_key], source=source).exists():
						# 	taxon.sources.add(OriginSource.objects.get_or_create(origin_id=line[taxon_id_key], source=source))
						create_origin_source(taxon, line[taxon_id_key], source)

				taxonomy = TaxonomicLevel.objects.find(taxon=line["originalName"])

				if taxonomy.count() == 0:
					raise Exception(f"Taxonomy not found.\n{line}")
				elif taxonomy.count() > 1:
					raise Exception(f"Multiple taxonomy found.\n{line}")

				if line["lat_lon"] and len(line["lat_lon"]) != 2:
					raise Exception(f"Bad formatting for lat_lon field\n{line}")

				os, new = OriginSource.objects.get_or_create(origin_id=line["sample_id"], source=source)
				if new:
					occ = Occurrence.objects.create(
						taxonomy=taxonomy.first(),
						batch=batch,
						voucher=line["voucher"],
						basis_of_record=Occurrence.TRANSLATE_BASIS_OF_RECORD.get(line["basisOfRecord"], Occurrence.UNKNOWN),
						collection_date_year=int(line["year"]) if line["year"] else None,
						collection_date_month=int(line["month"]) if line["month"] else None,
						collection_date_day=int(line["day"]) if line["day"] else None,
						geographical_location=find_gadm(line),
						decimal_latitude=float(line["lat_lon"][0]) if line["lat_lon"] else None,
						decimal_longitude=float(line["lat_lon"][1]) if line["lat_lon"] else None,
						coordinate_uncertainty_in_meters=int(line["coordinateUncertaintyInMeters"])
						if line["coordinateUncertaintyInMeters"]
						else None,
						elevation=int(line["elevation"]) if line["elevation"] else None,
						depth=int(line["depth"]) if line["depth"] else None,
					)
				else:
					occ = Occurrence.objects.get(sources=os)

				occ.sources.add(os)
