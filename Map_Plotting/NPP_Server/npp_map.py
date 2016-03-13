from __future__ import print_function

import pandas as pd
import datetime
import math
from bokeh.client import push_session
from bokeh.io import curdoc
from bokeh.models import WMTSTileSource,ImageSource
from bokeh.document import Document
from bokeh.tile_providers import STAMEN_TONER
from bokeh.plotting import show,Figure,figure
from bokeh.models.glyphs import Line
from bokeh.models import Range1d, ColumnDataSource, LinearAxis, PanTool, WheelZoomTool,HoverTool,VBox,HBox,Select,DataRange1d

TOOLS="pan,wheel_zoom,reset,save,hover"

document = Document()
session = push_session(document)

def geographic_to_web_mercator(x_lon, y_lat):     
    if abs(x_lon) <= 180 and abs(y_lat) < 90:          
        num = x_lon * 0.017453292519943295         
        x = 6378137.0 * num         
        a = y_lat * 0.017453292519943295          
        x_mercator = x         
        y_mercator = 3189068.5 * math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a)))         
        return x_mercator, y_mercator      
    else:         
        print('Invalid coordinate values for conversion') 


size = 'Days Active'
#read in data
df_geo = pd.read_csv('NPP_Locations.csv')
df_npp = pd.read_csv('NUREG_1350_Volume_27_Appendix_A.csv')
df= merged_data = pd.merge(left=df_geo,right=df_npp, left_on='NRCSiteName', right_on='Plant Name Unit Number') # merge data sets
x2 = list(range(len(df)))
y2 = list(range(len(df)))
for i in range(len(df)):
    x2[i],y2[i] = geographic_to_web_mercator(df['lon'][i],df['lat'][i])
df['merc_lat'] = x2
df['merc_lon'] = y2

source_map = ColumnDataSource(data=dict())

def map():
    x_range=(-10000000,-11000000)
    y_range=(3500000,5200000)

    plot=Figure(tools=TOOLS, title = 'Power Plant Locations',plot_width=1000,plot_height=500,
    x_range=x_range,y_range=y_range)
    plot.add_tile(STAMEN_TONER)
    plot.axis.visible = False
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.scatter(x="lat_b", y="lon_b",source=source_map,size="size",color='red', marker='o') 
    plot.scatter(x="lat_p", y="lon_p",source=source_map,size="size",color='blue', marker='square') 

    hover = plot.select(dict(type=HoverTool))
    hover.tooltips = [('Plant Name','@name'),('Reactor and Containment','@type')]

    return plot

df_perform = pd.read_csv('npp_performance.csv', index_col='Date')
locations = list(df_perform.columns.values)
location = 'Arkansas Nuclear 1'

source_perfomance = ColumnDataSource(data=dict())

def performance():
    plot = Figure(x_axis_type="datetime",tools="pan,hover", toolbar_location=None,title = 'Power Plant Performance',
                  plot_width=1000,plot_height=300)
    plot.line(x="time",y="power_out",source=source_perfomance,line_color="green")
    plot.x_range = DataRange1d(range_padding=0.0, bounds=None)
    return plot

def update_map():
    if size == 'Days Active':
        df['Commercial Operation'] = pd.to_datetime(df['Commercial Operation'])
        timediff = datetime.datetime.now() - df['Commercial Operation']
        days = timediff.dt.days
        df['Commercial Operation' + ' Days'] = days
        df['normalized_size'] = 15*(df['Commercial Operation Days']/df['Commercial Operation Days'].max())
    elif size == 'Days Remaining':
        df['Operating License Expires'] = pd.to_datetime(df['Operating License Expires'])
        timediff = datetime.datetime.now() - df['Operating License Expires']
        days = abs(timediff.dt.days)
        df['Operating License Expires' + ' Days'] = days
        df['normalized_size'] = 15*(df['Operating License Expires Days']/df['Operating License Expires Days'].max())    
    elif size == 'Power Output':
        df['normalized_size'] = 15*(df['Licensed MWt']/df['Licensed MWt'].max())

    #split data based on reactor type
    data_bwr = df[df['Reactor and Containment Type'].str.contains('BWR')]
    data_pwr = df[df['Reactor and Containment Type'].str.contains('PWR')]

    source_map.data = dict(
        lat_b=data_bwr['merc_lat'],
        lon_b=data_bwr['merc_lon'],
        lat_p=data_pwr['merc_lat'],
        lon_p=data_pwr['merc_lon'],
        size=df['normalized_size'],
        name=df['Plant Name Unit Number'],
        type=df['Reactor and Containment Type']
    )

def update_performance():
    npp_loc = df_perform[location]
    source_perfomance.data = dict(time=df_perform.index.to_datetime(), power_out=npp_loc)

def update_data():
    update_map()
    update_performance()

def on_size_change(attr, old, new):
    global size
    size=new
    update_data()

def on_location_change(attr, old, new):
    global location
    location = new
    update_data()

def create_layout():
    size_select = Select(value='Days Active', title='NPP Scaling', options=['Days Active', 'Days Remaining', 'Power Output'])
    size_select.on_change('value',on_size_change)
    
    location_select = Select(title="Power Plant", value="Arkansas Nuclear 1", options=locations)
    location_select.on_change('value', on_location_change)

    controls = HBox(children=[size_select,location_select])
    layout = VBox(children=[controls, map(),performance()])

    return layout

layout = create_layout()
update_data()

document.add_root(layout)
session.show(layout)

if __name__ == "__main__":
    print("\npress ctrl-C to exit")
    session.loop_until_closed()
