import exif
import ipyleaflet as ipl
import ipywidgets as ipw
from os import listdir


def from_dms(dms):
    d, m, s = dms
    return d + m / 60 + s / 3600


def get_geodata(pfile):
    img = exif.Image(pfile)
    lat = from_dms(img.gps_latitude)
    lon = from_dms(img.gps_longitude)
    elev = img.gps_altitude    
    return lat, lon, elev


def get_photos_geodata(pdir):
    photos = [p for p in listdir(pdir) if p.endswith(('jpg','JPG'))]
    pdict = {}    
    for pfile in photos:
        ppath = f'{pdir}/{pfile}'
        pdict[pfile] = get_geodata(ppath)
    return pdict


def photomarks(photodir, resized=True):
    pdict = get_photos_geodata(photodir)
    markers = []
    for pname in pdict:
        loc=pdict[pname]
        pmark = ipl.CircleMarker(location=loc, radius=6)
        ppath = f'{photodir}/resized/{pname}' if resized else f'{photodir}/{pname}'
        file = open(ppath, "rb")
        image = file.read()
        ipimg = ipw.Image(value=image, format='jpg')
        if not resized:
            ipimg.width=400
        pmark.popup = ipimg
        pmark.popup_min_width = 200
        markers.append(pmark)
    return ipl.MarkerCluster(markers=markers)
