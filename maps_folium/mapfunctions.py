import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from folium import Map, PolyLine, TileLayer, LayerControl, PolyLine, FeatureGroup, Circle
from folium.plugins import MarkerCluster
from gpxfunctions import read_osmand, dist_hv, correct_time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Basemaps
esri_sat = TileLayer(tiles='Esri.WorldImagery', name='Esri Sat')
mtb_map = TileLayer(tiles='MtbMap', name='Mtb Map CZ')
osm_map = TileLayer(tiles='OpenStreetMap.Mapnik', name='OpenStreet Map')


def trackmap(trkfile, name='track', zoom=13, color='green', simplify=False, add_track=True):
    lat, lon, elev, times = read_osmand(trkfile, simplify=simplify, trasa=True)
    (part_dist, delev) = dist_hv(lat, lon, elev)
    npts = len(lat)
    mapcenter = (sum(lat) / npts, sum(lon) / npts)
    mp = Map(location=mapcenter, zoom_start=14, tiles=None, width=800, height=600, control_scale=True)
    mp.add_child(esri_sat)
    mp.add_child(mtb_map)
    mp.add_child(osm_map)
    # mp.add_child(LayerControl())
    track = PolyLine(locations=list(zip(lat, lon)), weight=2, color=color, name=name, overlay=True)
    if add_track:
        track.add_to(mp)
    return mp, lat, lon, elev, correct_time(times), part_dist, track


def add_track(mp, trkfile, name, color='cyan', weight=2, simplify=False):
    lat, lon, elev, times = read_osmand(trkfile, simplify=simplify, trasa=True)
    (part_dist, delev) = dist_hv(lat, lon, elev)
    track = PolyLine(locations=list(zip(lat, lon)), color=color, fill=False, weight=weight, name=name)
    track.add_to(mp)
    return mp, lat, lon, elev, correct_time(times), part_dist, track


def plot_trackstats(trackdata):
    elev, times, pdists = trackdata
    figures = make_subplots(rows=2, cols=1, subplot_titles=("Čas. profil", "Vzdial. profil"))
    figures.add_trace(go.Scatter(x=times, y=elev, name='time'), row=1, col=1)
    figures.add_trace(go.Scatter(x=pdists, y=elev, name='dist'), row=2, col=1)  
    figures.update_layout(height=400, width=500)
    return figures


def plot_2tracks(tdata1, tdata2):
    elev, times, pdists = tdata1
    elev2, times2, pdists2 = tdata2
    figures = make_subplots(rows=2, cols=1, subplot_titles=("Čas. profil", "Vzdial. profil"))
    figures.add_trace(go.Scatter(x=times, y=elev, name='time'), row=1, col=1)
    figures.add_trace(go.Scatter(x=pdists, y=elev, name='dist'), row=2, col=1)
    figures.add_trace(go.Scatter(x=times2, y=elev2, name='time2'), row=1, col=1)
    figures.add_trace(go.Scatter(x=pdists2, y=elev2, name='dist2'), row=2, col=1)
    figures.update_layout(height=400, width=500)
    return figures
