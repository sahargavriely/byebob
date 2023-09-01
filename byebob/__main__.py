import contextlib
import datetime as dt
import json
import pathlib
import random
import time

from .webdriver import WebDriver


email = ''
password = ''
start_hour_range = 8, 10  # The range of hours which the day start submitting time will randomized from
hours_a_day_range = 9, 12  # The range of hours which the day will take will randomized from
headless = True
# headless = False
driver = WebDriver(email, password, headless=headless)

activity_log = dict()
activity_log_path = pathlib.Path('activity_log.json')
if activity_log_path.exists():
    with activity_log_path.open() as file:
        activity_log = json.load(file)
not_working_day = 'not_working_day'
cloack_in = 'cloack_in'
cloack_out = 'cloack_out'


def log_activity(key):
    if key is None:
        return
    timestamp, day = now_but_readable().split(' ')
    if day not in activity_log:
        activity_log[day] = dict()
    activity_log[day][key] = timestamp


def driver_action_wrapper(action, *args, log_key=None, **kwargs):
    # Check if the routine already occured in this day
    _, day = now_but_readable().split(' ')
    if log_key is not None and day in activity_log and log_key in activity_log[day]:
        print(f'{log_key!r} activity has already occured. Skipping action...')
        return
    global driver
    try:
        ret = action(*args, **kwargs)
        log_activity(log_key)
        return ret
    except KeyboardInterrupt:
        raise
    except Exception:
        pass
    with contextlib.suppress(Exception):
        driver.quit()
    print('\tSomething went wrong, relaunching driver')
    driver = WebDriver(email, password, headless=headless)
    ret = getattr(driver, action.__name__)(*args, **kwargs)
    log_activity(log_key)
    return ret


def progressbar(amount, prefix='', size=60):
    def show(j):
        x = int(size * j / amount)
        print(f'\t\t{prefix}[{u">" * x}{("." * (size - x))}] {j}/{amount}',
              end='\r', flush=True)
    show(0)
    for i in range(amount):
        yield i
        show(i + 1)
    print(flush=True)


def get_sec(wake_up_time):
    delta = wake_up_time - dt.datetime.now()
    sec = delta.days * 24 * 60 * 60 if delta.days else delta.seconds
    return sec


def progressbar_wrapper(wake_up_time, interval, label, sec):
    for _ in progressbar(sec // interval, label):
        sec -= interval
        if get_sec(wake_up_time) < sec:
            continue
        time.sleep(interval)


def sleep(wake_up_time: dt.datetime):
    sec = get_sec(wake_up_time)
    if sec > 60 * 60:
        progressbar_wrapper(wake_up_time, 60 * 60, 'Hours:  ', sec)
    elif sec > 60:
        progressbar_wrapper(wake_up_time, 60, 'Minutes:', sec)
    else:
        progressbar_wrapper(wake_up_time, 1, 'Seconds:', sec)


def hibernation(wake_up_time: dt.datetime):
    print('\tHibernating, see ya at:',
          wake_up_time.strftime('%H:%M:%S %d/%m/%Y'))
    while wake_up_time > dt.datetime.now() + dt.timedelta(seconds=60):
        sleep(wake_up_time)
    print('\tGood morning sunshine')


def now_but_readable(**kwargs):
    now = dt.datetime.now()
    if kwargs:
        now = now + dt.timedelta(**kwargs)
    return now.strftime('%H:%M:%S %d/%m/%Y')


def daily_routine():
    if driver_action_wrapper(driver.is_working_day):
        print('Clocking in, time:', now_but_readable())
        driver_action_wrapper(driver.clock_in, log_key=cloack_in)
        minimum, maximum = hours_a_day_range
        sec = random.randint(minimum * 60 * 60, maximum * 60 * 60)
        colck_out_time = dt.datetime.now() + dt.timedelta(seconds=sec)
        hibernation(colck_out_time)
        print('Clocking out, time:', now_but_readable())
        driver_action_wrapper(driver.clock_out, log_key=cloack_out)
        print('My work here is done for today')
    else:
        print('Not a working day, bye bye')


def next_run(next_day=1):
    tmrrw = dt.datetime.now() + dt.timedelta(days=next_day)
    minimum, maximum = start_hour_range
    t = random.randint(int(minimum * 60), int(maximum * 60))
    hour = t // 60
    minute = t % 60
    return dt.datetime(tmrrw.year, tmrrw.month, tmrrw.day, hour, minute)


try:
    hibernation(next_run(0))
    while True:
        daily_routine()
        hibernation(next_run())
except KeyboardInterrupt:
    driver.quit()
    exit()
finally:
    with activity_log_path.open('w') as file:
        json.dump(activity_log, file)
