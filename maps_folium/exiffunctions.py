import exif
import folium
from folium.plugins import MarkerCluster
from folium  import IFrame, LayerControl
from os import listdir
import base64

def from_dms(dms):
    d, m, s = dms
    return d + m / 60 + s / 3600


def get_geodata(pfile):
    img = exif.Image(pfile)
    lat = from_dms(img.gps_latitude)
    lon = from_dms(img.gps_longitude)
    elev = img.gps_altitude
    orient = 'portrait' if img.orientation == 6 else 'landscape'
    return lat, lon, elev, orient


def get_photos_geodata(pdir):
    photos = [p for p in listdir(pdir) if p.endswith(('jpg','JPG'))]
    pdict = {}    
    for pfile in photos:
        ppath = f'{pdir}/{pfile}'
        pdict[pfile] = get_geodata(ppath)
    return pdict


def mk_popup(fname, orient):
    encoded = base64.b64encode(open(fname,'rb').read())
    svg = """<object data="data:image/jpg;base64,{}" width="{}" height="{} type="image/svg+xml">
             </object>""".format
    if orient == 'portrait':
        width, height, fat_wh = 225, 300, 1.2
    else:
        width, height, fat_wh = 300, 225, 1.2
    iframe = IFrame(svg(encoded.decode('UTF-8'), width, height) , width=width*fat_wh, height=height*fat_wh)
    return folium.Popup(iframe, parse_html = True, max_width=400)
    

def photomarks(photodir, m):
    pdict = get_photos_geodata(photodir)
    markers = MarkerCluster(name='GPS body', spiderfyDistanceMultiplier=1.5)
    # bez posledneho parametra sa neukazu blizke popups
    for pname in pdict:
        lat, lon, elev, orient = pdict[pname]
        ppath = f"{photodir}/resized/{pname}"
        popup = mk_popup(ppath, orient)
        pmark = folium.CircleMarker(location=(lat, lon), radius=6, fill=True, popup=popup)
        pmark.add_to(markers)
    markers.add_to(m)
    LayerControl().add_to(m)
    return m
