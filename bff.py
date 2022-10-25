from datetime import timedelta
from mimetypes import init
from time import timezone
import requests
from bs4 import BeautifulSoup
from delorean import Delorean, parse


def convert_24_clock(s):
    am_or_pm = s[-2:].strip()

    # retrieve hour
    initial_time_hour = s[:-2].split(':')[0]
    initial_time_hour = int(initial_time_hour)

    if am_or_pm == 'pm' and initial_time_hour != 12:
        initial_time_hour += 12
    if am_or_pm == 'am' and initial_time_hour == 12:
        initial_time_hour = 0

    # retrieve minutes
    initial_time_minutes = s[:-2].split(':')[1]
    initial_time_minutes = int(initial_time_minutes)

    return [initial_time_hour, initial_time_minutes]


def get_bff_shows():
    print('hi')
    URL = "https://bff.fm/shows/schedule"
    d = Delorean()
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    scheduleItems = soup.findAll('article', attrs={'class': 'ShowScheduleColumn-item'})

    shows = []

    for item in scheduleItems:
        show = {}
        show['station'] = 'bff'
        deets = item['title']

        # show name
        show['show'] = deets.split('at')[0].strip()
        # dj
        show['dj'] = item.find('a', attrs={'itemprop': 'author'}).text

        # times
        times = deets.split(' at ')[-1].split(',')[0]

        try:
            # convert date into a datetime of timezone us/pacific
            show_date = parse(deets.split(' ')[-1].strip(), timezone='US/Pacific')

            # retrieve full datetime objects for start and end of show
            [begin_hour, begin_minute] = convert_24_clock(times.split('–')[0])
            begin_show_date = show_date.replace(hour=begin_hour, minute=begin_minute).shift('utc')

            [end_hour, end_minute] = convert_24_clock(times.split('–')[1])
            end_show_date = show_date.replace(hour=end_hour, minute=end_minute)
            if ('pm' in times.split('–')[0] and 'am' in times.split('–')[1]):
                end_show_date = (end_show_date + timedelta(days=1))
            end_show_date = end_show_date.shift('utc')

            show['begin_day'] = begin_show_date.naive.strftime('%w')
            show['begin_hour'] = begin_show_date.naive.hour
            show['begin_minute'] = begin_show_date.naive.minute

            show['end_day'] = end_show_date.naive.strftime('%w')
            show['end_hour'] = end_show_date.naive.hour
            show['end_minute'] = end_show_date.naive.minute

            show_link = item.find('a')
            show['show_link'] = show_link['href']
            shows.append(show)

        except Exception as e:
            print(f'This show date ({deets}) could not be parsed.')

    for show in shows:
        try:
            r = requests.get('https://bff.fm' + show['show_link'])
            soup = BeautifulSoup(r.content, 'html5lib')
            divs = soup.find_all('div')
            description_divs = []
            for div in divs:
                if 'RadioShow-description' in div['class'] and 'FormattedText' in div['class']:
                    show['description'] = div.text[2:-2].strip()

        except Exception as e:
            print(e)

    return shows


if __name__ == "__main__":
    shows = get_bff_shows()
    for show in shows:
        pass
        # def add_day(show_time, show_date):
        #     show_hour = int(show_time.split(':')[0])
        #     show_minute = int(show_time.split(':')[1])
        #     show_date = show_date.replace(hour=show_hour, minute=show_minute).shift(timezone='UTC').naive.strftime('%w')
        #     return [show_time, show_date]
        # if start is 'pm' and second is 'am', use tomorrow for end date day
