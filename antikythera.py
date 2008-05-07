# THE ANTIKYTHERA MECHANISM
# computes anything and everything you might care to know about calendars

import computus
import hebrew

import cgi
import cgitb

phase_names = [ 'New', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous',
        'Full', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent' ]

def get():
    cgitb.enable()
    form = cgi.FieldStorage()

    print 'Content-type: text/html'
    print
    interleave(int(form["year"].value))

def interleave(year):

    start_date = computus.gregorian_to_jd((year, 3, 1))
    end_date = computus.gregorian_to_jd((year, 5, 31))

    julian = julian_calendar(year)
    gregorian = gregorian_calendar(year)
    hebrew_cal = hebrew_calendar(hebrew.ad_to_am_at_pesach(year))
    compendium = easter_compendium(year)

    i_julian = 0
    i_hebrew = 0
    i = 0

    while julian[i_julian][0] != start_date: i_julian += 1
    while gregorian[i][0] != start_date: i += 1
    while hebrew_cal[i_hebrew][0] != start_date: i_hebrew += 1
    offset = i_julian - i
    hebrew_offset = i_hebrew - i

    # Find Sunday.
    while gregorian[i][3] != 0: i += 1

    print """
<div align="center">
<table border="1" cellspacing="0">
<tr>
<th width="100">Sunday</th>
<th width="100">Monday</th>
<th width="100">Tuesday</th>
<th width="100">Wednesday</th>
<th width="100">Thursday</th>
<th width="100">Friday</th>
<th width="100">Saturday</th>
"""
    done = False
    while not done:
        if gregorian[i][3] == 0:
            print '</tr>'
            print '<tr>'
        print '<td height="100" valign="top">'
        jd = gregorian[i][0]
        if jd == end_date: done = True
        print 'G',
        print_calendar_entry(gregorian[i])
        print '<br>'
        print 'J',
        print_calendar_entry(julian[i + offset])
        print '<br>'
        print 'H',
        print_hebrew_calendar_entry(
                hebrew_cal[i + hebrew_offset], gregorian[i][3])
        print '<br>'
        annotations = consult_compendium(compendium, jd)
        j_easter = False
        j_pre_easter = False
        for a in annotations:
            if a == 'gregorian_equinox': print 'Equinox (W)'
            elif a == 'gregorian_full_moon': print 'Full Moon (W)'
            elif a == 'gregorian_easter': print 'Easter (W)'
            elif a == 'julian_equinox': print 'Equinox (E)'
            elif a == 'julian_full_moon': print 'Full Moon (E)'
            elif a == 'julian_easter':
                print 'Easter (E)'
                j_easter = True
            elif a == 'julian_uncorrected_easter': j_pre_easter = True
            elif a == 'passover': print 'Passover'
            elif a == 'passover_prep': print 'Full Moon (H)'
            if j_pre_easter and not j_easter: print 'Not Easter (E)'
        print '</td>'
        i += 1

    print '''
</tr>
</table>
</div>
'''

def consult_compendium(compendium, jd):
    annotations = []
    for key in compendium:
        if compendium[key] == jd:
            annotations += [ key ]
    return annotations

def easter_compendium(year):
    gregorian_data = computus.gregorian_easter(year)
    julian_data = computus.julian_easter(year)
    compendium = {}
    for key in gregorian_data: compendium[key] = gregorian_data[key]
    for key in julian_data: compendium[key] = julian_data[key]
    return compendium

hebrew_month_names = [ 'Shevat', 'Adar', 'Adar I', 'Adar II', 'Nissan',
        'Iyar', 'Sivan' ]

def hebrew_calendar(year):
    is_leap = hebrew.is_leap(year)

    jd = hebrew.shevat_jd(year)
    adar_jd = hebrew.adar_jd(year)
    adar_i_jd = hebrew.adar_i_jd(year)
    nisan_jd = hebrew.nisan_jd(year)
    iyar_jd = hebrew.iyar_jd(year)
    sivan_jd = hebrew.sivan_jd(year)
    tamuz_jd = hebrew.tamuz_jd(year)

    calendar = []
    day = 1
    month = 0
        
    while True:
        calendar += [ (jd, month, day, dol_to_pom(day - 5)) ]
        jd += 1

        if is_leap and jd == adar_i_jd:
            month = 2
            day = 1
        elif is_leap and jd == adar_jd:
            month = 3
            day = 1
        elif (not is_leap) and jd == adar_jd:
            month = 1
            day = 1
        elif jd == nisan_jd:
            month = 4
            day = 1
        elif jd == iyar_jd:
            month = 5
            day = 1
        elif jd == sivan_jd:
            month = 6
            day = 1
        elif jd == tamuz_jd:
            break
        else:
            day += 1
    
    return calendar

def julian_calendar(year):
    return calendar(
            computus.julian_to_jd((year, 2, 1)),
            computus.julian_year(year),
            year % 4 == 0)

def gregorian_calendar(year):
    return calendar(
            computus.gregorian_to_jd((year, 2, 1)),
            computus.gregorian_year(year),
            is_gregorian_leap_year(year))

def is_gregorian_leap_year(year):
    if year % 100 == 0: return year % 400 == 0
    else: return year % 4 == 0

# HACK!
def dol_to_pom(day_of_lunation):
    phase = int((day_of_lunation + 4) / 3.5)
    if phase >= 8: phase = 0
    return phase

def calendar(initial_jd, year_data, leap):
    i_january_3 = computus.find_day(year_data, 1, 3)
    i_february_1 = computus.find_day(year_data, 2, 1)
    i_june_1 = computus.find_day(year_data, 6, 1)
    i_january_new_moon = computus.find_new_moon_after(
            i_january_3, year_data)

    calendar = []
    day_of_lunation = 32 - year_data[i_january_new_moon][1]
    phase = dol_to_pom(day_of_lunation)
    # HACK!
    day_of_phase = int((day_of_lunation + 4) % 3.5) + 1

    jd = initial_jd

    for i in range(i_february_1, i_june_1):
        (month, day, weekday, new_moon) = year_data[i]
        if new_moon:
            phase = 1
            day_of_phase = 1
        # Bissextile!
        if leap:
            if month == 1 or (month == 2 and day < 24): weekday -= 1
            if month == 2 and day == 24:
                calendar += [ (jd, 2, 24, (weekday - 1) % 7, phase) ]
                jd += 1
        calendar += [ (jd, month, day, weekday % 7, phase) ]
        day_of_phase += 1
        if day_of_phase == 5 - (phase % 2) and phase != 0:
            day_of_phase = 1
            phase += 1
        phase = phase % 8
        jd += 1

    return calendar

def print_calendar_entry(entry):
    (jd, month, day, weekday, phase) = entry
    mon_name = computus.months[month]
    print '%s %d' % (mon_name, day)

def print_hebrew_calendar_entry(entry, weekday):
    (jd, month, day, phase) = entry
    mon_name = hebrew_month_names[month]
    print '%d %s' % (day, mon_name)

def print_calendar(calendar):
    for entry in calendar: print_calendar_entry(entry)
