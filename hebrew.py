# Hebrew calendar
#
# Reference: http://www.shirhadash.org/calendar/abouthcal.html

def dhh_to_halakhim(days, hours, halakhim):
    return halakhim + 1080 * (hours + 24 * days)

def halakhim_to_wdhh(total_halakhim):
    total_hours = total_halakhim / 1080
    halakhim = total_halakhim % 1080
    total_days = total_hours / 24
    hours = total_hours % 24
    total_weeks = total_days / 7
    days = total_days % 7
    return (total_weeks, days, hours, halakhim)

day_length = dhh_to_halakhim(1, 0, 0)
month_length = dhh_to_halakhim(29, 12, 793)
creation = dhh_to_halakhim(2, 5, 204)

def months_before_year(year):
    metonic_cycles = ((year - 1) / 19) * 235
    r = (year - 1) % 19
    months = [
              0,  12,  24,  37,  49,  61,  74,  86,  99, 111,
                 123, 136, 148, 160, 173, 185, 197, 210, 222 ]
    return metonic_cycles + months[r]

def molad_tishrei(year):
    return creation + months_before_year(year) * month_length

def rosh_hashanah(year):
    molad = molad_tishrei(year)
    (weeks, days, hours, halakhim) = halakhim_to_wdhh(molad)
    if hours > 18:
        molad = molad + day_length
        (weeks, days, hours, halakhim) = halakhim_to_wdhh(molad)
    if ((not is_leap) and days == 3 and
            (hours >= 10 or (hours == 9 and halakhim > 204))):
        molad = molad + day_length
        (weeks, days, hours, halakhim) = halakhim_to_wdhh(molad)
    if (is_leap(year) and days == 2 and
            (hours >= 16 or (hours == 15 and halakhim > 589))):
        molad = molad + day_length
        (weeks, days, hours, halakhim) = halakhim_to_wdhh(molad)
    if days in [ 1, 4, 6 ]:
        molad = molad + day_length
        (weeks, days, hours, halakhim) = halakhim_to_wdhh(molad)
    return (weeks, days)

def is_leap(year):
    return (year % 19) in [ 0, 3, 6, 8, 11, 14, 17 ]

def wd_to_jd(weeks, days):
    return weeks * 7 + days + 347996

