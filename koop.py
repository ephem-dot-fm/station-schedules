from unicodedata import name
import requests
from delorean import Delorean, parse
import pytz

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# STILL TO DO:
# OO. Get times and add to Datetime object
# OO. Create the show object with show name etc.
# 3. Get description programmatically
# 4. Add those to shows array then pass in


def convert_to_24_hour_time(t, d):
    # if there are minutes, handle those
    time_has_minutes = False
    if ':' in t:
        time_has_minutes = True

    # get hours and minutes
    time_alone = t[:-2]
    if time_has_minutes:
        hour, minute = int(time_alone.split(':')[0]), int(time_alone.split(':')[1])
    elif not time_has_minutes:
        hour, minute = int(time_alone), 00

    # am or pm
    am_or_pm = t[-2:]

    # 12am counts as 0
    if am_or_pm == 'am' and hour == 12:
        hour = 0

    # if pm add 12
    if am_or_pm == 'pm' and hour != 12:
        hour += 12

    d = d.replace(hour=hour, minute=minute, second=0).shift('utc').naive

    day = d.strftime('%w')
    hour = d.hour
    minute = d.minute
    return (day, hour, minute)


def get_koop_shows():
    shows = []

    DRIVER_PATH = '/Users/maxmccready/Downloads/chromedriver'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    driver.get('https://koop.org/shows/')
    all_rows = driver.find_elements(By.CSS_SELECTOR, "tr")

    for row in all_rows:
        all_shows_in_row = row.find_elements(By.CLASS_NAME, "schedule-cell")

        for i, s in enumerate(all_shows_in_row[1:]):

            show = {
                'station': 'koop'
            }

            d = Delorean()
            d.shift('America/Chicago')

            match i:
                case 0:
                    d = d.next_sunday()
                case 1:
                    d = d.next_monday()
                case 2:
                    d = d.next_tuesday()
                case 3:
                    d = d.next_wednesday()
                case 4:
                    d = d.next_thursday()
                case 5:
                    d = d.next_friday()
                case 6:
                    d = d.next_saturday()

            try:
                name = s.find_element(By.CLASS_NAME, "show-name")
                show['show'] = name.text

                show_link = name.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
                show['show_link'] = show_link

                time = s.find_element(By.CLASS_NAME, "time").text

                begin, end = time.split('-')[0].strip(), time.split('-')[1].strip()
                (begin_day, begin_hour, begin_minute) = convert_to_24_hour_time(begin, d)
                (end_day, end_hour, end_minute) = convert_to_24_hour_time(end, d)

                show['begin_day'] = begin_day
                show['begin_hour'] = begin_hour
                show['begin_minute'] = begin_minute
                show['end_day'] = end_day
                show['end_hour'] = end_hour
                show['end_minute'] = end_minute

            except Exception as e:
                print('no show in slot')
                continue

            shows.append(show)

    for show in shows:
        # get dj and description
        try:
            driver.get(show['show_link'])

            # dj
            hosts = driver.find_element(By.CLASS_NAME, "program-hosts")
            dj = hosts.text[8:].strip()
            show['dj'] = dj

            # description
            description_div = driver.find_element(By.CLASS_NAME, "description")
            description_p_tags = description_div.find_elements(By.CSS_SELECTOR, "p")[:-1]
            description_text = ''

            for i, tag in enumerate(description_p_tags):
                if tag.text == "Latest show:" or tag.text == "More shows can be found on Mixcloud.":
                    continue
                else:
                    description_text += f' {tag.text}'

            show['description'] = description_text

        except Exception as e:
            print(e)

    driver.quit()
    return shows


if __name__ == "__main__":
    all_koop_shows = get_koop_shows()

    # DRIVER_PATH = '/Users/maxmccready/Downloads/chromedriver'
    # driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    # driver.get('https://koop.org/programs/free-samples/')

    # # dj
    # hosts = driver.find_element(By.CLASS_NAME, "program-hosts")
    # dj = hosts.text[8:].strip()

    # # description
    # description_div = driver.find_element(By.CLASS_NAME, "description")

    # description_p_tags = description_div.find_elements(By.CSS_SELECTOR, "p")[:-1]
    # print(f'Length of description_p_tags: {len(description_p_tags)}')

    # description_text = ''

    # for i, tag in enumerate(description_p_tags):
    #     if tag.text == "Latest show:" or tag.text == "More shows can be found on Mixcloud.":
    #         continue
    #     else:
    #         description_text += tag.text

    # print(f'DJ: {dj}')
    # print(f'Description: {description_text}')

    # driver.quit()
