import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as ipw
from datetime import datetime, timedelta
from ipyleaflet import Map, Polyline, basemaps, basemap_to_tiles
from ipyleaflet import ScaleControl, LayersControl
from gpxfunctions import read_osmand, dist_hv, correct_time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Basemaps
# pozri https://leaflet-extras.github.io/leaflet-providers/preview/
osmbase = basemaps.OpenStreetMap.Mapnik
openmap = basemap_to_tiles(osmbase)
openmap.name = 'OSM Mapnik'
mtbase = basemaps.MapTiler.Outdoor
mtbase['key'] = 'sxrepFSq1zmnE6UrD5dL'
maptiler = basemap_to_tiles(mtbase)
maptiler.name = 'MapTiler'
# mapbox = basemap_to_tiles(basemaps.MapBox)
# mapbox.accessToken = 'pk.eyJ1IjoibWlrZXNsIiwiYSI6ImNqbWQ0bmh3eTE1bzMza255bjJnaDRjZ2MifQ.LpGIQRQPcHHqzEX3CS7wYA'
# mapbox.name = 'Mapbox'
esri_sat = basemap_to_tiles(basemaps.Esri.WorldImagery)
esri_sat.name = 'Esri Sat'
mtbmap = basemap_to_tiles(basemaps.MtbMap)
mtbmap.name = 'MtbMap.cz'
# freemapsk = basemap_to_tiles(basemaps.FreeMapSK)
# freemapsk.name = 'Freemap.sk'
maptiler.base = esri_sat.base = mtbmap.base = openmap.base = True


def trackmap(trkfile, name='track', zoom=13, color='green',simplify=False, add_track=True):
    lat, lon, elev, times = read_osmand(trkfile, simplify=simplify, trasa=True)
    (part_dist, delev) = dist_hv(lat, lon, elev)
    npts = len(lat)
    mapcenter = (sum(lat) / npts, sum(lon) / npts)
    mp = Map(center=mapcenter, 
              zoom=zoom, layout=ipw.Layout(width='100%', height='600px'),
              layers=[maptiler, esri_sat, mtbmap, openmap])
    track = Polyline(locations=list(zip(lat, lon)), color=color, fill=False, weight=2, name=name)
    if add_track:
        mp.add(track)
    mp.add(ScaleControl(imperial=False, position='bottomright'))
    mp.add(LayersControl(position='topright'))
    return mp, lat, lon, elev, correct_time(times), part_dist, track


def add_track(mp, trkfile, name, color='cyan', weight=2, simplify=False):
    lat, lon, elev, times = read_osmand(trkfile, simplify=simplify, trasa=True)
    (part_dist, delev) = dist_hv(lat, lon, elev)
    track = Polyline(locations=list(zip(lat, lon)), color=color, fill=False, weight=weight, name=name)
    mp.add(track)
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
