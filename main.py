import psycopg2

from bff import get_bff_shows


def write_schedule_to_pg(station):
    conn = psycopg2.connect('postgresql://postgres:BBWjnHbbic4d0qoJnQYe@containers-us-west-46.railway.app:7052/railway')
    cursor = conn.cursor()

    # populate shows array
    shows = []

    if station == 'bff':
        shows = get_bff_shows()

    for show in shows:
        cursor.execute('INSERT INTO schedules (station, show, dj, begin_day, begin_hour, begin_minute, end_day, end_hour, end_minute) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                       (show['station'], show['show'], show['dj'], show['begin_day'], show['begin_hour'], show['begin_minute'], show['end_day'], show['end_hour'], show['end_minute']))

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    write_schedule_to_pg('bff')
