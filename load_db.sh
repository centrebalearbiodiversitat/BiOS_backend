for file in data/NO_BORRAR/GIS/*/*.shp
do
  echo "$file"
  python manage.py load_gadm "$file"
done
for file in data/NO_BORRAR/taxonomy/*/*.csv
do
  echo "$file"
  python manage.py load_taxonomy "$file"
done