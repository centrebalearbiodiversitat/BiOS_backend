# Geography
echo "Loading Autonomous communities..."
python manage.py load_gadm data/GIS/IDEIB_AC/*uncertainess*/*.shp
echo "Loading Islands..."
python manage.py load_gadm data/GIS/IDEIB_islands/*uncertainess*/*.shp
echo "Loading Municipalities..."
python manage.py load_gadm data/GIS/IDEIB_municipalities/*uncertainess*/*.shp
echo "Loading Populations..."
python manage.py load_gadm data/GIS/CNIG_poblaciones/*uncertainess*/*.shp

#Populate
echo "Populating tags..."
python manage.py populate_tags
echo "Populating habitats..."
python manage.py populate_habitats


for folder in data/groups/*/
do
  # Taxonomy
  echo "$folder/taxonomy.csv"
  python manage.py load_taxonomy_new "$folder/taxonomy.csv"

  # Images
  echo "$folder/images.json"
  python manage.py load_images "$folder/images.json"

  # IUCN
  echo "$folder/iucn.json"
  python manage.py load_taxon_data "$folder/iucn.json"

  # Tags
  echo "$folder/tags.xlsx"
  python manage.py load_taxon_tags "$folder/tags.xlsx"

  # Occurrences
  for file in "$folder/occurrences/"*.json
  do
    echo "$file"
    python manage.py load_occurrences_new_synonyms "$file"
  done

  # Genetics
  for file in "$folder/genetics/"*.json
  do
    echo "$file"
    python manage.py load_occurrences_new_synonyms "$file"
  done
done

echo "Loading basis..."
python manage.py load_basis data/basis.json
echo "Loading sources..."
python manage.py load_sources data/sources.csv