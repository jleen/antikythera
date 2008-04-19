# Compute the date of Easter according to various calendars.
#
# Reference: http://www.newadvent.org/cathen/05480b.htm
#
# Note that the table at the end of the section "Inaccuracy of the Metonic
# Cycle" has a misprint: all "+1" indications on or after year 4500 should be
# 100 years later than shown.  (The text above the table gets it right.)

import hebrew

##############################################
# Main entry point for the Gregorian calendar.

def gregorian_easter(year):
    return easter(gregorian_year(year))

def julian_easter(year):
    presumptive_easter = julian_to_jd((year, ) + easter(julian_year(year)))
    print 'Before Passover correction:', jd_to_gregorian(presumptive_easter)
    passover_begins = hebrew.pesach_jd(hebrew.ad_to_am_at_pesach(year))
    print '           Passover begins:', jd_to_gregorian(passover_begins)
    while (passover_begins > presumptive_easter):
        presumptive_easter += 7
    print ' After Passover correction:', jd_to_gregorian(presumptive_easter)
    return jd_to_gregorian(presumptive_easter)

def easter(year_data):
    i_vernal_equinox = find_vernal_equinox(year_data)
    i_paschal_new_moon = find_new_moon_after(i_vernal_equinox - 13, year_data)
    print 'Paschal new moon:', year_data[i_paschal_new_moon]

    # (Actually this is the day *after* the Paschal full moon, just as the rule
    # calls for.)

    i_paschal_full_moon = i_paschal_new_moon + 14
    i_easter = find_first_sunday_after(i_paschal_full_moon, year_data)
    return year_data[i_easter][0:2]


########################################
# Boring functions to scan the calendar.

def find_vernal_equinox(year_data):
    i = 0
    while 1:
        (month, day, weekday, new_moon) = year_data[i]
        if month == 3 and day == 21: return i
        i = i + 1

def find_new_moon_after(i, year_data):
    while 1:
        (month, day, weekday, new_moon) = year_data[i]
        if new_moon: return i
        i = i + 1

def find_first_sunday_after(i, year_data):
    while 1:
        (month, day, weekday, new_moon) = year_data[i]
        if weekday == 0: return i
        i = i + 1


##################################################
# The Metonic cycle and its Gregorian refinements.

def golden_number(year):
    r = (1 + year) % 19
    if r == 0: return 19
    else: return r

# The Gregorian epact is a base value determined in 1584, plus some
# refinements to correct for "jitter" in the lunar and solar calendars.

def gregorian_epact(year):
    raw = base_greg_epact(year) + lunar_equation(year) + solar_equation(year)
    return raw % 30

# The Metonic cycle merely counts by 11 mod 30, but somewhat arbitrarily
# loops back to the beginning after 19 entries, not the expected 30.

metonic_cycle = [ None,
        0, 11, 22, 3, 14, 25, 6, 17, 28, 9, 20, 1, 12, 23, 4, 15, 26, 7, 18 ]

def metonic_epact(year):
    return metonic_cycle[golden_number(year)]

# By the time of the Gregorian calendar, the epacts had already slipped by
# one day.

def base_greg_epact(year):
    return metonic_epact(year) + 1

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


###########################################
# Construct the static liturgical calendar.

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
        # conflict resolution.  (See hack25, below.)

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


#######################################
# Build the yearly liturgical calendar.

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

def second_julian_dominical(year):
    sol_num = solar_number(year)
    if sol_num ==  1: return 6
    if sol_num ==  2: return 5
    if sol_num ==  3: return 4
    if sol_num ==  4: return 3
    if sol_num ==  5: return 1
    if sol_num ==  6: return 7
    if sol_num ==  7: return 6
    if sol_num ==  8: return 5
    if sol_num ==  9: return 3
    if sol_num == 10: return 2
    if sol_num == 11: return 1
    if sol_num == 12: return 7
    if sol_num == 13: return 5
    if sol_num == 14: return 4
    if sol_num == 15: return 3
    if sol_num == 16: return 2
    if sol_num == 17: return 7
    if sol_num == 18: return 6
    if sol_num == 19: return 5
    if sol_num == 20: return 4
    if sol_num == 21: return 2
    if sol_num == 22: return 1
    if sol_num == 23: return 7
    if sol_num == 24: return 6
    if sol_num == 25: return 4
    if sol_num == 26: return 3
    if sol_num == 27: return 2
    if sol_num == 28: return 1

def solar_number(year):
    return ((year + 8) % 28) + 1

# Currently a hack: we ignore the Jan-Feb Dominical Letter for a leap year.
# Thus, we return the wrong values for those months.  That's fine if Easter
# is all we care about.
#
# Note that we're not inserting the leap day.  This is *not* a bug.  In the
# liturgical calendar, like the Roman calendar on which it's based, the
# intercalary day is treated as the first "half" of a 48-hour day, which is
# February 24, of all things.  (See Wikipedia s.v. "bissextile.")  The day of
# the week *does* change at the 24-hour mark, however, and that's when the leap
# year's second Dominical Letter takes effect.
#
# This is all very silly, but the important thing is that for the sake of
# the computation of moons, we always count 28 days in February.  When
# February 24 is doubled, its moon phase is doubled with it.

def gregorian_year(year):
    year_dom = second_gregorian_dominical(year)
    year_epact = gregorian_epact(year)

    # This is a hack too, but it's Aloysius Lilius's hack, not mine.  Somehow
    # it was considered very important that you never get the same new moon
    # two years in a row, so when that would happen, you move the second new
    # moon.

    hack25 = (year_epact == 25 and golden_number(year) > 11)
    return generic_year(year_dom, year_epact, hack25)

def julian_year(year):
    year_dom = second_julian_dominical(year)
    # TODO: I have no idea why the -2 is necessary.
    year_epact = metonic_epact(year - 2)
    return generic_year(year_dom, year_epact, hack25 = False)

def generic_year(year_dom, year_epact, hack25):
    days = []
    this_month = None
    this_day = None
    this_weekday = None
    this_new_moon = None

    for cal in calendarium:
        (month, day, dominical, epact) = cal

        if (this_month != month) or (this_day != day):
            if this_month != None:
                days += [(this_month, this_day, this_weekday, this_new_moon)]
            this_month = month
            this_day = day
            this_weekday = (dominical - year_dom) % 7
            this_new_moon = False

        if hack25:
            if epact == -25: this_new_moon = True
        else:
            if epact == year_epact: this_new_moon = True

    # Don't forget the last day of the year.

    days += [(this_month, this_day, this_weekday, this_new_moon)]
    return days

def julian_to_gregorian(date):
    return jd_to_gregorian(julian_to_jd(date))

def julian_to_jd((year, month, day)):
    return 367 * year - int(7 * (year + 5001 + int((month - 9) / 7.0)) / 4.0) \
            + int(275 * month / 9.0) + day + 1729777

def gregorian_to_jd((year, month, day)):
    return 367 * year - int(7 * (year + int((month + 9) / 12.0)) / 4.0) \
            - int(3 * (int((year + (month - 9) / 7.0) / 100.0) + 1) / 4) \
            + int(275 * month / 9) + day + 1721029

def jd_to_julian(jd):
    raise 'wheeeee!'

def jd_to_gregorian(jd):
    j = jd + 32044
    g = j / 146097
    dg = j % 146097
    c = (dg / 36524 + 1) * 3 / 4
    dc = dg - c * 36524
    b = dc / 1461
    db = dc % 1461
    a = (db / 365 + 1) * 3 / 4
    da = db - a * 365
    y = g * 400 + c * 100 + b * 4 + a
    m = (da * 5 + 308) / 153 - 2
    d = da - (m + 4) * 153 / 5 + 122
    year = y - 4800 + (m + 2) / 12
    month = (m + 2) % 12 + 1
    day = d + 1
    return (year, month, day)


##################
# Output niceties.

def format_cal_item(entry):
    (month, day, dominical, epact) = entry
    mon = name_month(month)[0:3]
    epnum = name_epact(epact)
    dom = letters[dominical]
    return '%s %2d %s %s' % (mon, day, dom, epnum)

def print_calendarium():
    for cal in calendarium:
        print format_cal_item(cal)

def format_day(day_tuple):
    (month, day, weekday, new_moon) = day_tuple
    mon = name_month(month)[0:3]
    wee = weekdays[weekday][0:3]
    formatted = '%s %s %2d' % (wee, mon, day)
    if (new_moon): formatted += ' (new moon)'
    return formatted

def print_year(year):
    for day in year:
        print format_day(day)

def format_easter_entry(day, year):
    return '%s, %d' % (format_day(day), year)
