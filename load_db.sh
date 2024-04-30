for file in data/NO_BORRAR/GIS/*/*.shp
do
  echo "$file"
  python manage.py load_gadm "$file"
done

for file in data/NO_BORRAR/taxonomy/240424/*.csv
do
  echo "$file"
  python manage.py load_taxonomy "$file"
done

for file in data/NO_BORRAR/taxonomy/29042024/*.csv
do
  echo "$file"
  python manage.py load_taxonomy "$file"
done