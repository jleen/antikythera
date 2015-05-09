#!/usr/bin/env python3
# coding=utf-8

from math import sin, cos, asin, acos, radians, pi, degrees
from PIL import Image

AXIAL_TILT = radians(23.44)
CHUNK_FACTOR = 16

# https://en.wikipedia.org/wiki/Solar_zenith_angle
def solar_zenith_angle(day, lat):
    decl = solar_declination(day)
    cos_theta = sin(lat) * sin(decl) + cos(lat) * cos(decl)
    return acos(cos_theta)

# https://en.wikipedia.org/wiki/Position_of_the_Sun#Declination_of_the_Sun_as_seen_from_Earth
# Circular approximation of Earth's orbit introduces ~1º error.
# "day" is ordinal starting at Jan 1 (10 days after solstice).
def fast_approx_solar_declination(day):
    return -1 * AXIAL_TILT * cos(2 * pi * (day + 10) / 365)

def solar_declination(day):
    return -1 * asin(0.39779 * cos(0.01720283777228211 * (day + 10)
                                   + 0.03340560188317147 * sin(0.01720283777228211 * (day - 2))))

im = Image.new('L', (365, 90))
for day in range(365):
    for lat in range(90):
        angle = 2 * pi - solar_zenith_angle(day - 10, radians(90 - lat))
        byte_angle = 256 * angle / (2 * pi)
        scaled_angle = max(0, 256 - 3 * (256 - byte_angle))
        chunked_angle = int((scaled_angle - CHUNK_FACTOR / 2)
                            / CHUNK_FACTOR) * CHUNK_FACTOR
        im.putpixel((day, lat), chunked_angle)

im.save('solar.png', 'PNG')
