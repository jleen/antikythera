# THE ANTIKYTHERA MECHANISM
# computes anything and everything you might care to know about calendars

import computus

phase_names = [ 'New', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous',
        'Full', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent' ]

def interleave(year):
    start_date = computus.gregorian_to_jd((year, 3, 1))
    end_date = computus.gregorian_to_jd((year, 5, 31))

    julian = julian_calendar(year)
    gregorian = gregorian_calendar(year)
    compendium = easter_compendium(year)

    i_julian = 0
    i = 0

    while julian[i_julian][0] != start_date: i_julian += 1
    while gregorian[i][0] != start_date: i += 1
    offset = i_julian - i

    done = False
    while not done:
        jd = gregorian[i][0]
        if jd == end_date: done = True
        print 'Day', jd
        print 'J',
        print_calendar_entry(julian[i + offset])
        print 'G',
        print_calendar_entry(gregorian[i])
        annotations = consult_compendium(compendium, jd)
        for a in annotations: print a + '!'
        print
        i += 1

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

def calendar(initial_jd, year_data, leap):
    i_january_3 = computus.find_day(year_data, 1, 3)
    i_february_1 = computus.find_day(year_data, 2, 1)
    i_june_1 = computus.find_day(year_data, 6, 1)
    i_january_new_moon = computus.find_new_moon_after(
            i_january_3, year_data)

    calendar = []
    day_of_lunation = 32 - year_data[i_january_new_moon][1]
    phase = int((day_of_lunation + 4) / 3.5)
    if phase >= 8: phase = 0
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
    day_name = computus.weekdays[weekday][0:3]
    mon_name = computus.months[month][0:3]
    phase_name = phase_names[phase]
    print '%s %s %2d %s' % (day_name, mon_name, day, phase_name)

def print_calendar(calendar):
    for entry in calendar: print_calendar_entry(entry)
