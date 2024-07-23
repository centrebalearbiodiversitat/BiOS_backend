# Geography
echo "Loading gadm"
python manage.py load_gadm data/NO_BORRAR/GIS/IDEIB_AC/*uncertainess*/*.shp
python manage.py load_gadm data/NO_BORRAR/GIS/IDEIB_islands/*uncertainess*/*.shp
python manage.py load_gadm data/NO_BORRAR/GIS/IDEIB_municipalities/*uncertainess*/*.shp
python manage.py load_gadm data/NO_BORRAR/GIS/CNIG_poblaciones/*uncertainess*/*.shp

# Taxonomy
for file in data/NO_BORRAR/taxonomy/*/*.csv
do
  echo "$file"
  python manage.py load_taxonomy "$file"
done

# Occurrences
for file in data/NO_BORRAR/occurrences/*/*.csv
do
  echo "$file"
  python manage.py load_occurrences "$file"
done

# Images
for file in data/NO_BORRAR/images/*.csv
do
  echo "$file"
  python manage.py load_images "$file"
done

# genetics
for file in data/NO_BORRAR/genetics/*/*/*.csv
do
  echo "$file"
  python manage.py load_occurrences "$file"
done
