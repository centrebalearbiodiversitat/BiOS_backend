# Geography
echo "Loading Autonomous communities..."
python manage.py load_gadm data/GIS/IDEIB_AC/*uncertainess*/*.shp
echo "Loading Islands..."
python manage.py load_gadm data/GIS/IDEIB_islands/*uncertainess*/*.shp
echo "Loading Municipalities..."
python manage.py load_gadm data/GIS/IDEIB_municipalities/*uncertainess*/*.shp
echo "Loading Populations..."
python manage.py load_gadm data/GIS/CNIG_poblaciones/*uncertainess*/*.shp

echo "Populating tags..."
python manage.py populate_tags
echo "Populating habitats..."
python manage.py populate_habitats


for folder in data/groups/*
do
  # Taxonomy
  python manage.py load_taxonomy_new "$folder/taxonomy.csv"

  # Images
  python manage.py load_images "$folder/images.json"

  # IUCN
  python manage.py load_taxon_data "$folder/iucn.json"

  # Occurrences
  for file in "$folder/occurrences/"*.json
  do
    echo "$folder/occurrences/"*.json
    python manage.py load_occurrences_new_synonyms "$file"
  done

  # Genetics
  for file in "$folder/genetics/"*.json
  do
    echo "$folder/genetics/"*.json
    python manage.py load_occurrences_new_synonyms "$file"
  done
done