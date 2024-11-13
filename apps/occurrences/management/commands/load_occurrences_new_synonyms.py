import datetime
import json
import geopandas as gpd

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.contrib.gis.geos import Point, GEOSGeometry
from apps.genetics.models import Sequence, Marker, Product
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
	("species", "speciesKey", TaxonomicLevel.SPECIES),
	("subspecies", "subspeciesKey", TaxonomicLevel.SUBSPECIES),
	("variety", "varietyKey", TaxonomicLevel.SUBSPECIES),
]

BIO_MARKERS = {
	"12s rrna",
	"16s rrna",
	"18s rrna",
	"cyt-b",
	"rubisco",
	"cytb",
	"coi",
	"cox2",
	"its",
	"rbcl",
	"cytochrome-b",
	"co1",
	"coii",
	"its1",
	"cox",
	"co2",
	"cox1",
	"coxii",
	"its2",
	"5.8s rrna",
	"coxi",
	"5,8s rrna",
	"matk",
	"atp6",
	"atp8",
	"nad1",
	"nad2",
	"nad3",
	"nad4",
	"nad5",
	"nadh1",
	"nadh2",
	"nadh3",
	"nadh4",
	"nadh5",
	"nd1",
	"nd2",
	"nd3",
	"nd4",
	"nd5",
	"histone3",
	"h3",
	"hist3",
}


def parse_line(line: dict):
	for key, value in line.items():
		try:
			line[key] = json.loads(value)
		except:
			pass  # is not json format

	return line


def genetic_sources(line: dict, batch, occ):
	source, _ = Source.objects.get_or_create(
		name__icontains=line["occurrenceSource"],
		data_type=Source.SEQUENCE,
		defaults={
			"name": line["occurrenceSource"],
			"accepted": True,
			"origin": Source.TRANSLATE_CHOICES[line["occurrenceOrigin"]],
			"url": None,
		},
	)

	os, new = OriginSource.objects.get_or_create(
		origin_id=line["sample_id"],
		source=source,
		defaults={
			"attribution": line["attribution"],
		},
	)
	if not new and not Sequence.objects.filter(sources=os, occurrence=occ).exists():
		raise Exception(f"OriginSource already exists\n{line}")

	seq = Sequence.objects.filter(sources=os, occurrence=occ)
	if seq.exists():
		if seq.count() > 1:
			raise Exception(f"Found more than one sequence\n{line}")
		seq = seq.first()
	else:
		seq = Sequence.objects.create(
			occurrence=occ,
			batch=batch,
			isolate=line["isolate"],
			definition=line["definition"],
			published_date=parse_datetime(line["date"]) if line["date"] else None,
		)
		seq.sources.add(os)

	for production in line["genetic_features"]:
		if production["gene"]:
			# if production["gene"] and production["gene"].lower() in BIO_MARKERS:
			product = None
			if production["product"]:
				product, _ = Product.objects.get_or_create(
					name__iexact=production["product"],
					defaults={
						"name": production["product"],
					},
				)

			marker, is_new = Marker.objects.get_or_create(
				name__iexact=production["gene"],
				defaults={
					"name": production["gene"],
					"batch": batch,
					"accepted": True,
				},
			)

			# if product and not marker.products.all().filter(name=product).exists():
			# 	marker.products.add(product)

			# if not marker.sources.filter(id=os.id).exists():
			# 	marker.sources.add(os)

			marker.save()
			seq.markers.add(marker)
	seq.save()


def create_origin_source(ref_model_elem, origin_id, source):
	os, new = OriginSource.objects.get_or_create(origin_id=origin_id, source=source)
	if new:
		ref_model_elem.sources.add(os)
		ref_model_elem.save()
	# else:
	# 	if not ref_model_elem.sources.filter(id=os.id).exists():
	# 		raise Exception(f"Origin id already assigned to another model. {ref_model_elem}, {ref_model_elem.sources}, {os}")


class Command(BaseCommand):
	help = "Loads occurrences from csv"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)
		parser.add_argument("-d", nargs="?", type=str, default=",")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		with open(file_name, "r") as file:
			data = json.load(file)
			cbb_scope_geometry = gpd.read_file("apps/occurrences/management/commands/geometry/sea_uncertainess_no_holes/sea_uncertainess_no_holes.shp").loc[0].geometry
			cbb_scope_geometry = GEOSGeometry(cbb_scope_geometry.wkt)
			batch = Batch.objects.create()

			line: dict
			for line in data:
				line = parse_line(line)

				if OriginSource.objects.filter(origin_id=line["sample_id"], source__name__icontains="NCBI").exists():
					# print(f"OriginSource already exists in NCBI\n{line['sample_id']}")
					continue

				source, _ = Source.objects.get_or_create(
					name__iexact=line["occurrenceSource"],
					data_type=Source.TAXON,
					defaults={
						"name": line["occurrenceSource"],
						"accepted": True,
						"origin": Source.TRANSLATE_CHOICES[line["occurrenceOrigin"]],
						"url": None,
					},
				)

				for taxon_key, taxon_id_key, taxon_rank in TAXON_KEYS:
					if line[taxon_key] and line[taxon_id_key]:
						taxon = TaxonomicLevel.objects.find(taxon=line[taxon_key]).filter(rank=taxon_rank)

						taxon_count = taxon.count()
						if taxon_count > 1:
							raise Exception(f"Found multiple taxa for {taxon_key}:{taxon_id_key}.\n{line}")
						elif taxon_count == 0:
							continue

						taxon = taxon.first()
						create_origin_source(taxon, line[taxon_id_key], source)

				taxonomy = TaxonomicLevel.objects.find(taxon=line["originalName"]).filter(rank=TaxonomicLevel.TRANSLATE_RANK[line["taxonRank"].lower()])
				taxon_count = taxonomy.count()
				if taxon_count == 0:
					raise Exception(f"Taxonomy not found.\n{line}")
				elif taxon_count > 1:
					raise Exception(f"Multiple taxonomy found.\n{line}")

				if line["lat_lon"]:
					if len(line["lat_lon"]) != 2:
						raise Exception(f"Bad formatting for lat_lon field\n{line}")
				else:
					del line["lat_lon"]

				source, _ = Source.objects.get_or_create(
					name__iexact=line["occurrenceSource"],
					data_type=Source.OCCURRENCE,
					defaults={
						"name": line["occurrenceSource"],
						"accepted": True,
						"origin": Source.TRANSLATE_CHOICES[line["occurrenceOrigin"]],
						"url": None,
					},
				)

				os, new = OriginSource.objects.get_or_create(
					origin_id=line["sample_id"],
					source=source,
					defaults={
						"attribution": line["attribution"],
					},
				)
				if new:
					location = (Point(list(reversed(line["lat_lon"])), srid=4326)) if line.get("lat_lon", None) else None
					occ = Occurrence.objects.create(
						taxonomy=taxonomy.first(),
						batch=batch,
						voucher=line["voucher"] if line["voucher"] else None,
						basis_of_record=Occurrence.TRANSLATE_BASIS_OF_RECORD.get(line["basisOfRecord"].lower() if line["basisOfRecord"] else "unknown", Occurrence.INVALID),
						collection_date_year=(int(line["year"]) if line["year"] and 1500 < line["year"] < 3000 else None),
						collection_date_month=(int(line["month"]) if line["month"] and 0 < line["month"] <= 12 else None),
						collection_date_day=int(line["day"]) if line["day"] and 0 < line["month"] <= 31 else None,
						location=location,
						coordinate_uncertainty_in_meters=(int(line["coordinateUncertaintyInMeters"]) if line["coordinateUncertaintyInMeters"] else None),
						elevation=int(line["elevation"]) if line["elevation"] else None,
						depth=int(line["depth"]) if line["depth"] else None,
						recorded_by=line["recordedBy"],
						in_cbb_scope=cbb_scope_geometry.intersects(location) if location else False,
					)
					occ.sources.add(os)
					occ.save()
				else:
					occ = Occurrence.objects.get(sources=os)

				if "genetic_features" in line:
					genetic_sources(line, batch, occ)
