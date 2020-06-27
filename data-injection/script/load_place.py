import csv
import psycopg2
import pandas as pd
import sys

#location
location_path = '../input/location/'
biggest_cities_csv = location_path + 'Biggest Cities in the World.csv'
new_york_location_csv = location_path + 'input/location/New_York_Tourist_Locations.csv'

#dataframe
location_header = ['id','location','parent_id']



#upload to db
