import gpxpy
from datetime import datetime, timedelta
import numpy as np

def osm_speed(waypoint):
    for extension in waypoint.extensions:
        if extension.tag == '{https://osmand.net}speed':
            return float(extension.text)
    return 0


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


def read_gpx(gfile):
    gpx_file = open(gfile, 'r')
    gpx = gpxpy.parse(gpx_file)
    lat, lon, elev = [], [], []
    # assume one track, one segment, data: lat, lon, elev
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lat.append(point.latitude)
                lon.append(point.longitude)
                elev.append(point.elevation)    
    return (lat, lon, elev)     

#  for converting route to track with time data

def dist_hv(lat, lon, elev):
    n = len(lat)
    hd = []
    lat_o, lon_o = lat[0], lon[0]
    for k in range(1, n):
        lat_n, lon_n = lat[k], lon[k]
        hd.append(gpxpy.geo.distance(lat_o, lon_o, None, lat_n, lon_n, None))
        lat_o, lon_o = lat_n, lon_n
    delev = np.diff(elev)
    partdists=[0] + list(np.cumsum(hd))
    return (partdists, delev) 

def trackstats(trackfile):
    lat, lon, elev, sp, times, hdop = read_osmand(trackfile)
    hd, delev = dis_hv(lat, lon, elev)
    tot_hd = hd[-1]
    tot_time = to_hms((times[-1] -times[0]).seconds) 
    hi_dist = sum((p for p in delev if p > 0.3))
    lo_dist = sum((p for p in delev if p < 0.3))
    return tot_hd, tot_time, hi_dist, lo_dist

def to_sec(ptime):
    return max(1, int(3600 * ptime))

def to_hms(ptime):  # hour, min, sec
    hh, ms = divmod(ptime, 3600)
    mm, ss = divmod(ms, 60)
    return hh, mm, ss

def to_dms(ptime):   # degrees, min, sec
    deg, minsec = divmod(ptime, 1)
    mnt, decsec = divmod(minsec, 1 / 60)
    return deg, mnt, 3600 * decsec

def from_dms(d, m, s):
    return d + m / 60 + s /3600


def part_time(hd, delev, hspeed, aspeed, dspeed):
    th = hd / hspeed
    tv = delev / aspeed if delev > 0 else -delev / dspeed
    if th > tv:
        max_t, other = th, tv
    else:    
        max_t, other = tv, th
    ptime = to_sec(max_t + 0.5 * other)
    return ptime


def tracktime(hd, delev, hspeed, aspeed, dspeed):
    tt = 0
    tpoc = timedelta(seconds=0)
    t0 = tpoc + datetime(2023, 1, 1, 0, 0, 0)
    tvals=[t0]
    for ahd, adel in zip(hd, delev):
        tp = part_time(ahd, adel, hspeed, aspeed, dspeed)
        tt += tp
        h, m, s = to_hms(tt)
        tvals.append(datetime(2023, 1, 1, h, m, s))
    return to_hms(tt), tvals


def write_times(trkfile, trkname, hspeed=4000, aspeed=400, dspeed=600):
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_track.name = trkname
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    lat, lon, elev = read_gpx(trkfile)
    hd, delev = dist_hv(lat, lon, elev)
    tt, tvals = tracktime(hd, delev, hspeed, aspeed, dspeed)
    for alat, alon, aelev, atime in zip(lat, lon, elev, tvals):
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(alat, alon, elevation=aelev, time=atime))
    outname = trkfile[:-4] + "_times.gpx"
    ofl = open(outname, 'w')
    ofl.write(gpx.to_xml())
    ofl.close()

def correct_time(times):
    ct = lambda t: datetime(t.year, t.month, t.day, t.hour + 2, t.minute, t.second, 0, None)
    return list(map(ct, times))
    