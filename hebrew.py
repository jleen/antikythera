# Hebrew Anno Mundi calendar
#
# Reference: http://www.shirhadash.org/calendar/abouthcal.html


########################
# Units and conversions.

# It's convenient to think in several sets of units.  We can talk about the
# number of halakhim since the epoch (a halakhim is 1/1080 of an hour), or the
# number of days:hours:halakhim, or weeks:days:hours:halakhim.  If we're just
# identifying a day, we can talk about total days, or weeks:days.  The
# week is a useful unit because it lets us read off the day of the week from
# the remaining days.
#
# Note that, for reasons your rabbi may be able to explain, Day 1 is a day
# and a half before the first reckoned moon, and almost a year before the
# Fiat Lux.  The date of creation isn't of interest to us here, but the date
# of the first moon is immensely interesting.  Notice that the length of a
# month is not an integral number of days.  Also, the round-off rules are fun.
# But we'll get to that later.

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
first_moon = dhh_to_halakhim(2, 5, 204)

am_epoch = 347996

def wd_to_jd((weeks, days)):
    return weeks * 7 + days + am_epoch

###########
# New year.

# We calculate Rosh Hashanah, the Jewish New Year's Day, by first counting up
# the right number of months since Day 1 (12 or 13 months per year, depending
# on intercalations)...

def months_before_year(year):
    metonic_cycles = ((year - 1) / 19) * 235
    r = (year - 1) % 19
    months = [
              0,  12,  24,  37,  49,  61,  74,  86,  99, 111,
                 123, 136, 148, 160, 173, 185, 197, 210, 222 ]
    return metonic_cycles + months[r]

def molad_tishrei(year):
    return first_moon + months_before_year(year) * month_length

# But then there are some rather complex rules by which we can "postpone"
# Rosh Hashanah if the moon is too late in the day, or if the year would be
# starting on a "bad" day, i.e. one which would cause certain festivals to
# fall on forbidden days of the week, later in the year.

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

#########
# Pesach.

# Now we can finally calculate the beginning of Passover.  It's simply the 15th
# of Nisan, but between 1 Tishrei and 15 Nisan there are three possible
# intercalations: a missing day in defective years, an extra day in excessive
# years, and the leap month of Adar I in leap years (which may themselves be
# defective, excessive, or neither).
#
# Excessive or defective years arise simply because of the complex round-off
# and postponement rules for Rosh Hashanah.  The simplest way to calculate
# them is to just compute next year's Rosh Hashanah and see how many days are
# between now and then.

length_4 = 30 + 29 + 30 + 29
length_shevat = 30
length_adar_i = 30
length_adar = 29
length_nisan = 30
length_iyar = 29

days_to_pesach = 30 + 29 + 30 + 29 + 30 + 29 + 14

def shevat_jd(year):
    rosh_hashanah_jd = wd_to_jd(rosh_hashanah(year))
    next_rh_jd = wd_to_jd(rosh_hashanah(year + 1))
    adar_i = length_adar_i * is_leap(year)
    excess = (next_rh_jd - rosh_hashanah_jd) - (354 + adar_i)
    return rosh_hashanah_jd + length_4 + excess

def adar_jd(year):
    return shevat_jd(year) + length_shevat + (length_adar_i * is_leap(year))

def adar_i_jd(year):
    return shevat_jd(year) + length_shevat

def nisan_jd(year):
    return adar_jd(year) + length_adar

def pesach_jd(year):
    return nisan_jd(year) + 14

def iyar_jd(year):
    return nisan_jd(year) + length_nisan

def sivan_jd(year):
    return iyar_jd(year) + length_iyar

# Cheesy Anno Domini to Anno Mundi conversion which punts the issue of the
# different New Years' Days by being pegged to Passover.

def ad_to_am_at_pesach(ad):
    return ad + 3760
