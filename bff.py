from datetime import timedelta
from mimetypes import init
from time import timezone
import requests
from bs4 import BeautifulSoup
from delorean import Delorean, parse

URL = "https://bff.fm/shows/schedule"
d = Delorean()
r = requests.get(URL)
soup = BeautifulSoup(r.content, 'html5lib')
scheduleItems = soup.findAll('article', attrs={'class': 'ShowScheduleColumn-item'})


def convert_24_clock(s):
    am_or_pm = s[-2:].strip()
    initial_time_hour = s[:-2].split(':')[0]
    initial_time_hour = int(initial_time_hour)
    initial_time_minutes = s[:-2].split(':')[1]

    if am_or_pm == 'pm' and initial_time_hour != 12:
        initial_time_hour += 12
    initial_time_hour = str(initial_time_hour)

    if initial_time_minutes == '30':
        return (initial_time_hour + ':30')
    else:
        return (initial_time_hour + ':00')


def add_day(show_time, show_date):
    show_hour = int(show_time.split(':')[0])
    show_minute = int(show_time.split(':')[1])
    show_date = show_date.replace(hour=show_hour, minute=show_minute).shift(timezone='UTC').naive.strftime('%w')
    return [show_time, show_date]
    # if start is 'pm' and second is 'am', use tomorrow for end date day


for item in scheduleItems:
    show = {}
    deets = item['title']
    show['show'] = deets.split('at')[0].strip()
    show['dj'] = item.find('a', attrs={'itemprop': 'author'}).text
    times = deets.split('at')[1].split(',')[0]
    try:
        show_date = parse(deets.split(' ')[-1].strip(), timezone='US/Pacific')
    except Exception as e:
        print(f'This show date ({deets}) could not be parsed.')

    try:
        show['start_time'] = convert_24_clock(times.split('–')[0])
        show['start_time'] = add_day(show['start_time'], show_date)

        show['end_time'] = convert_24_clock(times.split('–')[1])
        if ('pm' in times.split('–')[0] and 'am' in times.split('–')[1]):
            show['end_time'] = add_day(show['end_time']), (show_date + timedelta(days=1))
        else:
            show['end_time'] = add_day(show['end_time'], (show_date))
    except Exception as e:
        print(e)

    print(show)
