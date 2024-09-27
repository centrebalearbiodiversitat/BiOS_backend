# Geography
echo "Loading gadm"
python manage.py load_gadm data/NO_BORRAR/GIS/IDEIB_AC/*uncertainess*/*.shp
python manage.py load_gadm data/NO_BORRAR/GIS/IDEIB_islands/*uncertainess*/*.shp
python manage.py load_gadm data/NO_BORRAR/GIS/IDEIB_municipalities/*uncertainess*/*.shp
python manage.py load_gadm data/NO_BORRAR/GIS/CNIG_poblaciones/*uncertainess*/*.shp

# Taxonomy
#for file in data/NO_BORRAR/taxonomy_2/*/*.csv
#do
#  echo "$file"
#  python manage.py load_taxonomy_new "$file"
#done

# Taxon data
python manage.py populate_habitats
for file in data/NO_BORRAR/iucn/*/*.json
do
  echo "$file"
  python manage.py load_taxon_data "$file"
done

# Occurrences
for file in data/NO_BORRAR/occurrences/*/*.json
do
  echo "$file"
  python manage.py load_occurrences_new "$file"
done

# Images
for file in data/NO_BORRAR/images/*/*.json
do
  echo "$file"
  python manage.py load_images "$file"
done

# genetics
for file in data/NO_BORRAR/genetics/*/*.json
do
  echo "$file"
  python manage.py load_occurrences_new "$file"
done