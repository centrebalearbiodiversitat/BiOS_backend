import json, re
import geopandas as gpd
from django.core.management.base import BaseCommand
from django.db import transaction
from dateutil import parser
from django.contrib.gis.geos import Point, GEOSGeometry
from apps.genetics.models import Sequence, Marker
from apps.occurrences.models import Occurrence
from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import Batch, OriginId, Source
from common.utils.utils import get_or_create_source, get_or_create_source_with_dataset_key

GBIF = "gbif"
EXTERNAL_ID = "sample_id"
INTERNAL_NAME = "occurrenceSource"
SOURCE_TYPE = "occurrenceOrigin"

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
			pass

	return line

def genetic_sources(line: dict, batch, occ):
    source = get_or_create_source(
        source_type=Source.TRANSLATE_SOURCE_TYPE[line[SOURCE_TYPE]],
        extraction_method=Source.API,
        data_type=Source.SEQUENCE,
        batch=batch,
        internal_name=line[INTERNAL_NAME],
    )

    os, new = OriginId.objects.get_or_create(
        external_id=line[EXTERNAL_ID],
        source=source,
        defaults={
            "attribution": line["attribution"],
        },
    )
    if not new and not Sequence.objects.filter(sources=os, occurrence=occ).exists():
        raise Exception(f"OriginId already exists\n{line}")

    seq = None

    for production in line["genetic_features"]:
        if production["gene"]:
            normalized_gene_name = re.sub(r"[-\s_]", "", production["gene"].lower())
            if normalized_gene_name in BIO_MARKERS:

                marker, is_new = Marker.objects.get_or_create(
                    name__iexact=production["gene"],
                    defaults={
                        "name": production["gene"],
                        "batch": batch,
                        "accepted": True,
                        "product": production["product"],
                    },
                )

                marker.save()

                if seq is None:
                    seq = Sequence.objects.create(
                        occurrence=occ,
                        batch=batch,
                        isolate=line["isolate"],
                        definition=line["definition"],
                        published_date=parser.parse(line["date"]) if line["date"] else None,
                    )
                    seq.sources.add(os)

                seq.markers.add(marker)
                seq.save()


def create_origin_id(ref_model_elem, external_id, source):
	os, new = OriginId.objects.get_or_create(external_id=external_id, source=source)
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
				if OriginId.objects.filter(external_id=line[EXTERNAL_ID], source__basis__name__icontains="NCBI").exists():
					continue

				source = get_or_create_source(
					source_type=Source.TRANSLATE_SOURCE_TYPE[line[SOURCE_TYPE]],
					extraction_method=Source.API,
					data_type=Source.TAXON,
					batch=batch,
					internal_name=line[INTERNAL_NAME],
				)
					
				parent_level = ""
				for taxon_key, taxon_id_key, taxon_rank in TAXON_KEYS:
					if line[taxon_key] and line[taxon_id_key]:
						taxon = TaxonomicLevel.objects.find(taxon=line[taxon_key]).filter(rank=taxon_rank)
						taxon_count = taxon.count()
						# If there are taxon collisions, then try again with the parent
						if taxon_count > 1:
							taxon = TaxonomicLevel.objects.find(taxon=f"{parent_level} {line[taxon_key]}").filter(rank=taxon_rank)
							taxon_count = taxon.count()

						if taxon_count > 1:
							raise Exception(f"Found multiple taxa for {taxon_key}:{taxon_id_key}.\n{line}")
						elif taxon_count == 0:
							continue

						taxon = taxon.first()
						create_origin_id(taxon, line[taxon_id_key], source)
						parent_level = line[taxon_key]

				taxonomy = TaxonomicLevel.objects.find(taxon=line["originalName"]).filter(rank=TaxonomicLevel.TRANSLATE_RANK[line["taxonRank"].lower()])
				taxon_count = taxonomy.count()
				if taxon_count > 1:
					taxonomy = TaxonomicLevel.objects.find(taxon=f"{parent_level} {line['originalName']}").filter(rank=TaxonomicLevel.TRANSLATE_RANK[line["taxonRank"].lower()])
					taxon_count = taxon.count()

				if taxon_count == 0:
					raise Exception(f"Taxonomy not found.\n{line}")
				elif taxon_count > 1:
					raise Exception(f"Multiple taxonomy found.\n{line}")

				if line["lat_lon"]:
					if len(line["lat_lon"]) != 2:
						raise Exception(f"Bad formatting for lat_lon field\n{line}")
				else:
					del line["lat_lon"]
				source = get_or_create_source(
					source_type=Source.TRANSLATE_SOURCE_TYPE[line[SOURCE_TYPE]],
					extraction_method=Source.API,
					data_type=Source.OCCURRENCE,
					batch=batch,
					internal_name=line[INTERNAL_NAME],
				)

				if source.basis.internal_name == GBIF:
					internal_name = line[INTERNAL_NAME]
					dataset_key = line['datasetKey']

					os_new = get_or_create_source_with_dataset_key(internal_name, dataset_key, batch)

				os, new = OriginId.objects.get_or_create(
					external_id=line[EXTERNAL_ID],
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
						in_geography_scope=cbb_scope_geometry.intersects(location) if location else False,
					)
					
					if source.basis.internal_name == GBIF:
						if os_new:
							occ.sources.add(os_new)
					else:
						occ.sources.add(os)
					occ.save()
				else:

					occ = Occurrence.objects.get(sources=os)

					if source.basis.internal_name == GBIF:
						if os_new:
							occ.sources.add(os_new)

				if "genetic_features" in line:
					genetic_sources(line, batch, occ)
