#!/usr/bin/env python

import exif
import gpxpy
from os import listdir, mkdir
from os.path import isdir
from datetime import datetime, timedelta
import sys

# gpx functions

def osm_speed(waypoint):
    for extension in waypoint.extensions:
        if extension.tag == '{https://osmand.net}speed':
            return float(extension.text)
    return 0


# nacita korektne z Locus map, OSMAnd, aj export z Garminu
# predpokladame jednu trasu (track) a jeden segment
def read_osmand(gfile, simplify=False, trasa=False):
    gpx_file = open(gfile, 'r')
    gpx = gpxpy.parse(gpx_file)
    creator = gpx.creator
    if simplify:
        gpx.simplify(simplify)
    lat, lon, elev, sp, times, hdop = [], [], [], [], [], []
    # assume one track, one segment, written by OSMAnd
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lat.append(point.latitude)
                lon.append(point.longitude)
                times.append(point.time)
                elev.append(point.elevation)
                if 'OsmAnd' in creator:
                    sp.append(osm_speed(point))
                hdop.append(point.horizontal_dilution)
        times = correct_time(times)        
    return (lat, lon, elev, sp, times, hdop) if not trasa else  (lat, lon, elev, times)  

def to_dms(ptime):   # degrees, min, sec
    deg, minsec = divmod(ptime, 1)
    mnt, decsec = divmod(minsec, 1 / 60)
    return deg, mnt, 3600 * decsec


def correct_time(times):
    ct = lambda t: datetime(t.year, t.month, t.day, t.hour + 2, t.minute, t.second, 0, None)
    return list(map(ct, times))


# exif functions
def get_photodates(pdir):
    photos, dates = [], []
    for pfile in sorted(listdir(pdir)):
        with open(f'{pdir}/{pfile}', 'rb') as image_file:
            img = exif.Image(image_file)
        dt = img.datetime_original
        photos.append(pfile)
        dates.append(datetime.strptime(dt, '%Y:%m:%d %H:%M:%S'))
    return photos, dates


def nearest_time(phtime, times):
    for k, gt in enumerate(times):
        if gt < phtime:
            continue
        else:
            break
    k += 1        
    d_lo, d_hi =  phtime - times[k-1], times[k] - phtime
    return (k - 1) if (d_lo < d_hi) else k


def add_geodata(pfile, lat, lon, elev, k):
    img = exif.Image(pfile)
    img.gps_latitude = to_dms(lat[k])
    img.gps_latitude_ref = "N"
    img.gps_longitude = to_dms(lon[k])
    img.gps_longitude_ref = "E"
    img.gps_altitude = elev[k]  # in meters
    img.gps_altitude_ref = exif.GpsAltitudeRef.ABOVE_SEA_LEVEL
    return img


def add_photos_geodata(pdir, trkfile):
    lat, lon, elev, gdt = read_osmand(trkfile, simplify=2, trasa=True)
    photos, ptimes = get_photodates(pdir)
    outdir = f'{pdir}_geo'
    if not isdir(outdir):
        mkdir(outdir)
    for pfile, pdt in zip(photos, ptimes):
        k = nearest_time(pdt, gdt)
        img = add_geodata(f'{pdir}/{pfile}', lat, lon, elev, k)
        with open(f'{outdir}/{pfile}', 'wb') as new_image_file:
            new_image_file.write(img.get_file())
     

if len(sys.argv) != 3:
    print("Usage: add_geodata photos_dir gpx_trackfile")
    exit(1)

add_photos_geodata(sys.argv[1], sys.argv[2])

# Priklad volania: add_geodata fotky/VFKlak trasy/VFKlakouki.gpx
# Fotky s geotagmi budu v adresari fotky/VFKlak_geo, povodny adresar ostane nezmeneny
