# Compute the date of Easter according to various calendars.
#
# Reference: http://www.newadvent.org/cathen/05480b.htm
# Note that the table at the end of the section "Inaccuracy of the Metonic
# Cycle" has a misprint: all "+1" indications on or after year 4500 should be
# 100 years later than shown.  (The text above the table gets it right.)

def gregorian_easter(year):
    pass

def epact(year):
    raw = gregorian_epact(year) + lunar_equation(year) + solar_equation(year)
    return raw % 30

metonic_cycle = [
        18, 0, 11, 22, 3, 14, 25, 6, 17, 28, 9, 20, 1, 12, 23, 4, 15, 26, 7 ]

def metonic_epact(year):
    return metonic_cycle[golden_number(year)]

def gregorian_epact(year):
    return metonic_epact(year) + 1

def golden_number(year):
    r = (1 + year) % 19
    if r == 0: return 19
    else: return r

def lunar_equation(year):
    d = (year - 1500) / 2500
    r = (year - 1500) % 2500
    if r < 300:  return 8 * d
    if r < 600:  return 8 * d + 1
    if r < 900:  return 8 * d + 2
    if r < 1200: return 8 * d + 3
    if r < 1500: return 8 * d + 4
    if r < 1800: return 8 * d + 5
    if r < 2100: return 8 * d + 6
    if r < 2400: return 8 * d + 7
    return 8 * d + 8

def solar_equation(year):
    if year < 1600: return 0
    d = (year - 1600) / 400
    r = (year - 1600) % 400
    if r < 100: return  0 - (3 * d)
    if r < 200: return -1 - (3 * d)
    if r < 300: return -2 - (3 * d)
    return -3 - (3 * d)
