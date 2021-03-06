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

TOOLS="pan,wheel_zoom,save,hover"
TOOLS2 = "save"
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
shapes =["circle","square"]
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

source_map_bwr = ColumnDataSource(data=dict())
source_map_pwr = ColumnDataSource(data=dict())

def map():
    x_range=(-10000000,-11000000)
    y_range=(3500000,5200000)

    plot=Figure(tools=TOOLS, title = 'Power Plant Locations',plot_width=1000,plot_height=500,
    x_range=x_range,y_range=y_range)
    plot.add_tile(STAMEN_TONER)
    plot.axis.visible = False
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    m1=plot.circle(x="lat", y="lon",source=source_map_bwr,size="size",fill_alpha=0, line_width=2,color='red')
    m2=plot.square(x="lat", y="lon",source=source_map_pwr,size="size",fill_alpha=0, line_width=2,color='red')
    plot.select(dict(type=HoverTool)).tooltips = [('Plant Name','@name'),('Reactor and Containment','@type')]

    return plot

df_perform = pd.read_csv('npp_performance.csv', index_col='Date')
df_perform['average_perform'] = df_perform.mean(axis=1)
locations = list(df_perform.columns.values)
location = 'Arkansas Nuclear 1'

source_perfomance = ColumnDataSource(data=dict())

def performance():
    plot = Figure(x_axis_type="datetime",tools="save", toolbar_location=None,plot_width=1000,plot_height=300)
    l1=plot.line(x="time",y="power_out",source=source_perfomance,line_color="green",name='local')
    plot.add_tools(HoverTool(renderers=[l1]))
    plot.select(dict(type=HoverTool)).tooltips = [('Date','@hover_time'),('Performance','@power_out')]
    l2=plot.line(x="time",y="avg_perf",source=source_perfomance,line_color="red",name='global')
    plot.x_range = DataRange1d(range_padding=0.0, bounds=None)
    plot.title = "Plant Performance"
    return plot

def update_map():
    if size == 'Days Active':
        df['Commercial Operation'] = pd.to_datetime(df['Commercial Operation'])
        timediff = datetime.datetime.now() - df['Commercial Operation']
        days = timediff.dt.days
        df['Commercial Operation' + ' Days'] = days
        df['normalized_size'] = 20*(df['Commercial Operation Days']/df['Commercial Operation Days'].max())
    elif size == 'Days Remaining':
        df['Operating License Expires'] = pd.to_datetime(df['Operating License Expires'])
        timediff = datetime.datetime.now() - df['Operating License Expires']
        days = abs(timediff.dt.days)
        df['Operating License Expires' + ' Days'] = days
        df['normalized_size'] = 20*(df['Operating License Expires Days']/df['Operating License Expires Days'].max())    
    elif size == 'Power Output':
        df['normalized_size'] = 20*(df['Licensed MWt']/df['Licensed MWt'].max())

    df_bwr = df[df['Reactor and Containment Type'].str.contains("BWR")]
    df_pwr = df[df['Reactor and Containment Type'].str.contains("PWR")]

    source_map_bwr.data = dict(
        lat=df_bwr['merc_lat'],
        lon=df_bwr['merc_lon'],
        size=df_bwr['normalized_size'],
        name=df_bwr['Plant Name Unit Number'],
        type=df_bwr['Reactor and Containment Type'],
    )

    source_map_pwr.data = dict(
        lat=df_pwr['merc_lat'],
        lon=df_pwr['merc_lon'],
        size=df_pwr['normalized_size'],
        name=df_pwr['Plant Name Unit Number'],
        type=df_pwr['Reactor and Containment Type'],
    )


def update_performance():
    npp_loc = df_perform[location]
    source_perfomance.data = dict(time=df_perform.index.to_datetime(),power_out=npp_loc,hover_time=df_perform.index,
        avg_perf=df_perform['average_perform'])

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
    size_select = Select(value='Days Active', title='Marker Scaling:', options=['Days Active', 'Days Remaining', 'Power Output'])
    size_select.on_change('value',on_size_change)
    
    location_select = Select(title="Power Plant Name:", value=location, options=locations)
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
