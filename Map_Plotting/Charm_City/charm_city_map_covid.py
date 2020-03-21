import pandas as pd
import requests
import time
import folium
import pathlib

from folium.plugins import MarkerCluster
from matplotlib import pylab
from pylab import *

from opencage.geocoder import OpenCageGeocode
from pprint import pprint

key = 'add your own Open Cage Code key here'
geocoder = OpenCageGeocode(key)


file = pathlib.Path('South_Baltimore_Business_Status_COVID19_Update.csv')
if not file.exists ():
  lat = []
  lng = []

  df0 = pd.read_csv('South_Baltimore_Business_Status_COVID19.csv',encoding = "ISO-8859-1")
  df1 = df0.loc[:, ['Business_Name', 'Address']]
  df1['Address'] = df1['Address']+', Baltimore, MD'

  for i in range(len(df1)):
    ADDRESS = df1['Address'][i]
    result = geocoder.geocode(ADDRESS, no_annotations='1')
    temp = result[0]['geometry']['lat']
    lat.append(result[0]['geometry']['lat'])
    lng.append(result[0]['geometry']['lng'])
    time.sleep(0.5)

  lat = pd.DataFrame(lat)
  lng = pd.DataFrame(lng)
  df0['Latitude'] = lat
  df0['Longitude'] = lng
  df0.to_csv('South_Baltimore_Business_Status_COVID19_Update.csv')


df2 = pd.read_csv('South_Baltimore_Business_Status_COVID19_Update.csv',encoding = "ISO-8859-1")
df2 = df2[df2.Status != 'CLOSED']
# df2['category'] = 'other'

# central coordinates of Baltimore
EDI_COORDINATES = (39.2904, -76.6122)

# create empty map zoomed in on Baltimore
map = folium.Map(location=EDI_COORDINATES, zoom_start=12)
spots = MarkerCluster(name='spots').add_to(map)

def makeHref(url,link_text = None):
    if link_text == None:
        link_text = str(url)
    return '<a href="' + url + '"target="_blank">' + re.sub(r"[']+", "\\\\'", link_text[:45]) +'</a>'

def popopHTMLString(df2):
    '''input: a series that contains a url somewhere in it and generate html'''
    html =  makeHref(df2.Website, df2.Business_Name)
    return html

def plotDot(df2):
    htmlString = folium.Html(popopHTMLString(df2), script=True)
    folium.Marker(location=[df2.Latitude, df2.Longitude],
                        popup = folium.Popup(htmlString),
                        fill_color='#000000').add_to(spots)

#use df.apply(,axis=1) to iterate through every row in your dataframe
df2.apply(plotDot, axis = 1)
map.fit_bounds(map.get_bounds())
folium.LayerControl().add_to(map)
  
fn = 'south_baltimore_covid.html'
map.save(fn)
