import pandas as pd
import requests

import folium
from folium.plugins import MarkerCluster
from matplotlib import pylab
from pylab import *

def query_address(address):
    """Return response from open streetmap.
    
    Parameter:
    address - address of establishment
    
    Returns:
    result - json, response from open street map
    """
    
    url = "https://nominatim.openstreetmap.org/search"
    parameters = {'q':'{}, Baltimore'.format(address), 'format':'json'}
    
    response = requests.get(url, params=parameters)
    # don't want to raise an error to not stop the processing
    # print address instead for future inspection
    if response.status_code != 200:
        print("Error querying {}".format(address))
        result = {}
    else:
        result = response.json()
    return result

def define_category(mytype):
    if mytype in ['cafe', 'bakery', 'deli', 'ice_cream']:
        category = 1
    elif mytype in ['restaurant', 'pub', 'bar', 'fast_food']:
        category = 2
    else:
        category = 3
    return category

def flag_premise(premisename, category):
    """Flag premise according to its name.
    
    Parameter: 
    premisename - str
    
    Returns:
    ans - boolean
    """
    prem = str(premisename).lower()
    if ((category == 'coffeeshop' and ('caf' in prem 
                                       or 'coffee' in prem 
                                       or 'Tea' in str(premisename) 
                                       or 'bake' in prem 
                                       or 'bagel' in prem 
                                       or 'roast' in prem))
         or 
        (category == 'restaurant' and ('restaurant' in prem 
                                       or 'bar ' in prem 
                                       or 'tavern' in prem 
                                       or 'cask' in prem 
                                       or 'pizza' in prem
                                       or 'whisky' in prem
                                       or 'kitchen' in prem
                                       or 'Arms' in str(premisename)
                                       or 'Inn' in str(premisename) 
                                       or 'Bar' in str(premisename)))):
        ans = True
    else:
        ans = False
    return ans


df0 = pd.read_csv('charm_city_locations.csv')
df1 = df0.loc[:, ['Name', 'Address']]

df1['json'] = df1['Address'].map(lambda x: query_address(x))

df2 = df1[df1['json'].map(lambda d: len(d)) > 0].copy()

df2['lat'] = df2['json'].map(lambda x: x[0]['lat'])
df2['lon'] = df2['json'].map(lambda x: x[0]['lon'])
df2['type'] = df2['json'].map(lambda x: x[0]['type'])

df2['category'] = df2['type'].map(lambda mytype: define_category(mytype))

df2['is_coffeeshop'] = df2['Name'].map(lambda x: flag_premise(x, category='coffeeshop'))
df2['is_restaurant'] = df2['Name'].map(lambda x: flag_premise(x, category='restaurant'))

df2.loc[df2.is_restaurant, 'category'] = 2
df2.loc[df2.is_coffeeshop, 'category'] = 1

df2.to_csv('charm_location_data.csv')
# 
# # central coordinates of Edinburgh
# EDI_COORDINATES = (39.2904, -76.6122)
# 
# # create empty map zoomed in on Edinburgh
# map = folium.Map(location=EDI_COORDINATES, zoom_start=12)
# 
# # add one markercluster per type to allow for individual toggling
# coffeeshops = MarkerCluster(name='coffee shops').add_to(map)
# restaurants = MarkerCluster(name='pubs and restaurants').add_to(map)
# other = MarkerCluster(name='other').add_to(map)
# 
# # add coffeeshops to the map
# for chairs in df2[df2.category == 1].iterrows():
#     folium.Marker(location=[float(chairs[1]['lat']), float(chairs[1]['lon'])], 
#                   popup=chairs[1]['Name'],
#                  icon=folium.Icon(color='green', icon_color='white', icon='coffee', angle=0, prefix='fa')).add_to(coffeeshops)
# 
# # add pubs and restaurants to the map
# for chairs in df2[df2.category == 2].iterrows():
#     folium.Marker(location=[float(chairs[1]['lat']), float(chairs[1]['lon'])], 
#                   popup=chairs[1]['Name'],
#                  icon=folium.Icon(color='blue', icon='glass', prefix='fa')).add_to(restaurants)
# 
# # add other to the map
# for chairs in df2[df2.category == 3].iterrows():
#     folium.Marker(location=[float(chairs[1]['lat']), float(chairs[1]['lon'])], 
#                   popup=chairs[1]['Name'],
#                  icon=folium.Icon(color='gray', icon='question', prefix='fa')).add_to(other)
# 
# # enable toggling of data points
# folium.LayerControl().add_to(map)
# 
# fn = 'charm_city_locales.html'
# map.save(fn)
