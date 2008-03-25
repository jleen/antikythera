# Compute the date of Easter according to various calendars.
#
# Reference: http://www.newadvent.org/cathen/05480b.htm
#
# Note that the table at the end of the section "Inaccuracy of the Metonic
# Cycle" has a misprint: all "+1" indications on or after year 4500 should be
# 100 years later than shown.  (The text above the table gets it right.)

def gregorian_easter(year):
    pass

def gregorian_epact(year):
    raw = base_greg_epact(year) + lunar_equation(year) + solar_equation(year)
    return raw % 30

# The Metonic cycle merely counts by 11 mod 30, but somewhat arbitrarily
# loops back to the beginning after 19 entries, not the expected 30.
# Classically the Cycle is 1-based; I transpose Meton's final entry to the
# head of the list to make it 0-based.

metonic_cycle = [
        18, 0, 11, 22, 3, 14, 25, 6, 17, 28, 9, 20, 1, 12, 23, 4, 15, 26, 7 ]

def metonic_epact(year):
    return metonic_cycle[golden_number(year)]

# By the time of the Gregorian calendar, the epacts had already slipped by
# one day.

def base_greg_epact(year):
    return metonic_epact(year) + 1

def golden_number(year):
    r = (1 + year) % 19
    if r == 0: return 19
    else: return r

# Compensate for the Metonic Cycle's built-in inaccuracy: the ratio of a lunar
# to a solar year isn't really a rational number!

def lunar_equation(year):
    d = (year - 1500) / 2500
    r = (year - 1500) % 2500
    return (8 * d) + (r / 300)

# Compensate for the "missing" leap years in the Gregorian calendar.

def solar_equation(year):
    if year < 1600: return 0
    d = (year - 1600) / 400
    r = (year - 1600) % 400
    return (-3 * d) - (r / 100)


def month_length(month):
    if month == 2: return 28
    if month in [ 1, 3, 5, 7, 8, 10, 12]: return 31
    return 30

def build_calendarium():
    calendarium = []
    month = 1
    day = 1
    dominical = 1
    epact = 0
    lunation_parity = 1

    for x in range(365):
        calendarium += [ (month, day, dominical, epact) ]

        # We'll use -25 to indicate the special label for epact 24/25
        # conflict resolution.

        if ((lunation_parity == 1 and epact == 25) or
                (lunation_parity == 0 and epact == 26)):
            calendarium += [ (month, day, dominical, -25) ]

        if lunation_parity == 0 and epact == 25:
            epact -= 1
            calendarium += [ (month, day, dominical, epact) ]  # Again.

        day += 1
        if day > month_length(month):
            day = 1
            month += 1
            lunation_parity = not lunation_parity

        dominical += 1
        if dominical == 8: dominical = 1
        
        epact -= 1
        if epact == -1: epact = 29

    return calendarium

calendarium = build_calendarium()

months = [
        None, 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December' ]

numerals = [
        '*', 'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
        'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx',
        'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv', 'xxvi', 'xxvii', 'xxviii',
        'xxix', 'xxx' ]

letters = [
        None, 'A', 'B', 'C', 'D', 'E', 'F', 'G' ]

weekdays = [
        'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday' ]

def name_month(month): return months[month]

def name_epact(epact):
    if epact == -25: return '25'
    return numerals[epact]

def format_cal_item(entry):
    (month, day, dominical, epact) = entry
    mon = name_month(month)[0:3]
    epnum = name_epact(epact)
    dom = letters[dominical]
    return '%s %2d %s %s' % (mon, day, dom, epnum)

def print_calendarium():
    for cal in calendarium:
        print format_cal_item(cal)

# The "second" Dominical Letter is the one that takes effect after the leap
# day of a leap year.  This formula finds the (only) Dominical Letter of a
# non-leap year, or the second Dominical Letter of a leap year.
#
# Reference: http://www.newadvent.org/cathen/05109a.htm

def second_gregorian_dominical(year):
    a = year + 1
    b = year / 4
    c = year / 100 - 16
    d = c / 4
    e = a + b + d - c
    f = e % 7
    return 7 - f

# Currently a hack: we ignore the Jan-Feb Dominical Letter for a leap year.
# Thus, we return the wrong values for those months.  That's fine if Easter
# is all we care about.

def gregorian_year(year):
    year_dom = second_gregorian_dominical(year)
    year_epact = gregorian_epact(year)
    days = []
    for cal in calendarium:
        (month, day, dominical, epact) = cal
        weekday = (dominical - year_dom) % 7
        new_moon = (epact == year_epact)
        days += [(month, day, weekday, new_moon)]
    return days

def format_day(day_tuple):
    (month, day, weekday, new_moon) = day_tuple
    mon = name_month(month)[0:3]
    wee = weekdays[weekday][0:3]
    formatted = '%s %s %2d' % (wee, mon, day)
    if (new_moon): formatted += ' (new moon)'
    return formatted

def print_year(year):
    for day in gregorian_year(year):
        print format_day(day)
