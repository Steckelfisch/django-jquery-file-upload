# -*- coding: utf-8 -*-
import os
import datetime as dt
import math
import requests
from time import mktime

from django.conf import settings

import logging

logger = logging.getLogger(__name__)




def date_generator(start, end):
    from_date = start
    while from_date <= end:
        yield from_date
        from_date = from_date + dt.timedelta(days=1)


# from http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def get_date_time_from_filename(sound_file_name):
    '''
       filter date and time from filename.
       A valid date_time object is Truthy
       return 'False' if date or time are not recognized.

       accepts fineanes of the form: bm_-3.683166_40.479336_20141120_115503_0
       will return
       date_part: 20141120
       time_part: 115503

    '''
    date_part = None
    time_part = None
    logger.info("get_date_time_from_filename test: " + sound_file_name)
    filename, file_extension = os.path.splitext(sound_file_name)
    for file_part in filename.split('_'):
        logger.info("get_date_time_from_filename test_part: " + str(file_part))
        if date_part is None:
            try:
                date_part = dt.datetime.strptime(file_part, "%Y%m%d")
                continue
            except ValueError as ve:
                logger.info("get_date_time_from_filename (date): " + str(file_part) + "  " + str(ve))
                # pass

        if time_part is None:
            try:
                time_part = dt.datetime.strptime(file_part, "%H%M%S")
                time_part = dt.time(time_part.hour, time_part.minute, time_part.second)
                continue
            except ValueError as ve:
                logger.info("get_date_time_from_filename (time): " + str(file_part) + "  " + str(ve))
                # pass

        if date_part is not None and time_part is not None:
            # time_zone = pytz.timezone('Europe/Amsterdam')
            # return 'aware' datetime
            # return time_zone.localize( dt.datetime.combine(date_part, time_part))
            datetime_found = dt.datetime.combine(date_part, time_part)
            logger.info("datetime_found: "+str(datetime_found))
            return datetime_found
        else:
            logger.info("date_part: "+str(date_part)+" time_part: "+str(time_part))

    return False


def get_date_time_from_file(path_filename):
    '''

    :param path_filename:
    :return: the time at GMT (on Ubuntu 16.04)
    '''
    mtime = os.path.getmtime(path_filename)
    file_date_time = dt.datetime.fromtimestamp(mtime)

    # time_zone = pytz.timezone('Europe/Amsterdam')
    # return time_zone.localize( file_date_time )

    # return file_date_time
    return dt.datetime(file_date_time.year, file_date_time.month, file_date_time.day,
                       file_date_time.hour, file_date_time.minute, file_date_time.second)


def decimal_truncate(decimal_in):
    # in decimal
    # out truncated decimal as string
    # in: 2.1234567890 out 2.123456
    # in: -34.123456 out -34.123456
    before_dot_after = str(decimal_in).split(".")
    return before_dot_after[0] + "." + before_dot_after[1][:6]


def rename_to_batmusic_standard(path_filename, location, date_and_time, try_count):
    '''
     Standard is bm_<lat>_<lon>_<date_time>_<sub_index>.wav
    :param path_filename:
    :param location:
    :param date_and_time:
    :param try_count:
    :return:
    '''
    # set precicion to 12.123456
    trunc_lat = decimal_truncate(location.geometry.x)
    trunc_lon = decimal_truncate(location.geometry.y)
    milliseconds = try_count * 1000
    new_filename = 'bm_' + \
                   str(trunc_lat) + '_' + str(trunc_lon) + '_' + \
                   date_and_time.strftime('%Y%m%d') + '_' + \
                   date_and_time.strftime('%H%M%S') + '_' + \
                   str(milliseconds) + '.wav'
    return new_filename


def check_dst_correction_required_from_google(location, date_and_time):
    seconds_since_epoch = mktime(date_and_time.timetuple()) + (1e-6 * date_and_time.microsecond)
    url = "https://maps.googleapis.com/maps/api/timezone/json?location={0},{1}&timestamp={2}".format(location.geometry.y,
                                                                                                     location.geometry.x,
                                                                                                     seconds_since_epoch)
    if settings.GOOGLE_API_KEY:
        url += "&key=" + settings.GOOGLE_API_KEY
    result = requests.get(url)
    logger.info(str(result.json()))
    return 0


def is_completely_inside(start_time_1, end_time_1, start_time_2, end_time_2):
    '''
       returns True if timespan for start_time to end_time completely lies
                    in the timespan of this object:
                start1-end1 ____|-----------------|___
                start2-end2 ________|--------|________
                start2-end2 ____|-----------------|___
       returns False otherwise
    '''
    if start_time_2 >= start_time_1 and end_time_1 >= end_time_2:
        return True
    return False


def is_completely_outside(start_time_1, end_time_1, start_time_2, end_time_2):
    '''
       returns True if timespan for start_time to end_time completely lies
                    outside the timespan of delivery-pickup
              start1-end1 ______________|------|_______________
              start2-end2 __|--------|_________________________
              start2-end2 __|-----------|______________________
              start2-end2 _____________________|-----------|___
              start2-end2 ________________________|------|_____
       returns False otherwise
    '''
    # todo: require start_time < end_time
    # completely after self.pickup_time
    #   or completely before self.delivery_time
    if start_time_2 >= end_time_1 or start_time_1 >= end_time_2:
        return True
    return False


def partial_overlap(start_time_1, end_time_1, start_time_2, end_time_2):
    '''
        returns True if any overlap
        returns false otherwise
    '''
    # todo: require start_time < end_time
    if (is_completely_outside(start_time_1, end_time_1, start_time_2, end_time_2) or
       is_completely_inside(start_time_1, end_time_1, start_time_2, end_time_2)):
        return False
    return True


def between_start_end(date_and_time, dst_start, dst_end):
    if dst_start <= date_and_time <= dst_end:
        return True
    return False


def get_dst_correction(location, date_and_time, date_and_time_in_dst=False):
    '''
    :param location: timezone to check date_and_time against
    :param date_and_time: date_and_time to check
    :param date_and_time_in_dst: date_and_time is in DST
    :return: 0 if no correction required
             -x if x hours(change to seconds?) must be subtracted
             y if y hours(change to seconds?) must be added
    '''
    tz = location.timezone
    dst_start = None
    dst_end = None
    tz_transition_iter = iter(tz._utc_transition_times)
    for transition_time in tz_transition_iter:
        if date_and_time.year == transition_time.year:
            logger.debug(u"transition time: " + str(transition_time))
            dst_start = transition_time
            dst_end = tz_transition_iter.__next__()
            break

    #logger.error(u'dst_start: ' + unicode(dst_start) + u'   dst_end: ' + unicode(dst_end))

    if dst_start and dst_end:
        if date_and_time_in_dst:
            # als voor dst_start of na dst_end
            # (niet tussen dst_start en dst_end)
            if not between_start_end(date_and_time, dst_start, dst_end):
                return 1
        else:
            # als tussen dst_start en dst_end
            if between_start_end(date_and_time, dst_start, dst_end):
                return -1
    else:
        logger.debug("No DST for given timezone.")
    # no changes needed
    return 0



# =======================
def xxx_rename_to_batmusic_standard(path_filename, date_and_time):
    milliseconds = int(date_and_time.strftime('%f')) / 1000
    new_filename = 'bm_' + date_and_time.strftime('%Y%m%d') + '_' + date_and_time.strftime('%H%M%S') + '_' + str(
        milliseconds) + '.wav'
    # os.rename(path_filename, new_filename)
    return new_filename


def backup_rename_to_batmusic_standard(path_filename, date_and_time, try_count):
    milliseconds = try_count * 1000
    new_filename = 'bm_' + date_and_time.strftime('%Y%m%d') + '_' + date_and_time.strftime('%H%M%S') + '_' + str(
        milliseconds) + '.wav'
    return new_filename
