from calendar import weekday
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from delorean import Delorean
import pytz


def calculate_day(t, wkday):
    d = Delorean()
    d.shift('Europe/Dublin')

    match wkday.lower():
        case 'monday':
            d = d.next_monday()
        case 'tuesday':
            d = d.next_tuesday()
        case 'wednesday':
            d = d.next_wednesday()
        case 'thursday':
            d = d.next_thursday()
        case 'friday':
            d = d.next_friday()
        case 'saturday':
            d = d.next_saturday()
        case 'sunday':
            d = d.next_sunday()

    hour, minute = int(t.split(':')[0]), int(t.split(':')[1])
    d = d.replace(hour=hour, minute=minute, second=0)
    d = d.shift('utc').naive
    day = int(d.strftime('%w'))
    hour = d.hour
    minute = d.minute
    return (day, hour, minute)


def get_ddr_shows():
    shows = []

    DRIVER_PATH = '/Users/maxmccready/Downloads/chromedriver'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    driver.get('https://listen.dublindigitalradio.com/schedule')

    timeout = 5
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "show-title"))
        WebDriverWait(driver, timeout).until(element_present)

        # get all links for days of week
        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        all_day_links = driver.find_elements(By.CLASS_NAME, "nav-link")
        for link in all_day_links:
            if link.text in weekdays:
                link.click()
            else:
                continue

            # organize by class = px-4
            show_times_and_titles = driver.find_elements(By.CLASS_NAME, "px-4")
            for show in show_times_and_titles:
                show_details = {}

                # show name
                title = show.find_element(By.CLASS_NAME, "show-title")
                title = title.text

                # show time and date
                time = show.find_element(By.CLASS_NAME, "ddr-box-and-border-right")
                time = time.text
                begin, end = time.split('-')[0], time.split('-')[1]
                (begin_day, begin_hour, begin_minute) = calculate_day(begin, link.text)
                (end_day, end_hour, end_minute) = calculate_day(end, link.text)
                if begin_hour > end_hour:
                    end_day += 1
                if end_hour > begin_hour:
                    end_day = begin_day

                show_details['station'] = 'ddr'
                show_details['show'] = title
                show_details['dj'] = ''
                show_details['begin_day'] = begin_day
                show_details['begin_hour'] = begin_hour
                show_details['begin_minute'] = begin_minute
                show_details['end_day'] = end_day
                show_details['end_hour'] = end_hour
                show_details['end_minute'] = end_minute
                shows.append(show_details)

    except TimeoutException:
        print("Timed out waiting for page to load")

    return shows


if __name__ == "__main__":
    print(get_ddr_shows())
    # print(pytz.all_timezones)
