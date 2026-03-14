import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django_apscheduler.jobstores import register_events, register_job

import sys
from artistic.models import Judge, Start, Value, Competition, Config, Event, Person
from datetime import datetime, timedelta
from django.conf import settings
from pytz import timezone

# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler()

# This is the function you want to schedule - add as many as you want and then register them in the start() function below
def calculate_start_time():
    if (int(Config.get_config_value('timetrack')) > 0):
        act = Config.get_config_value('start_id')
        s = Start.objects.get(id=act)
        scheduled_time = s.scheduled_time.astimezone(timezone(settings.TIME_ZONE)).time()
        time_scheduled = (int(scheduled_time.strftime("%H"))*60)+int(scheduled_time.strftime("%M"))
        time_calculated = (int(s.calculated_time.strftime("%H"))*60)+int(s.calculated_time.strftime("%M"))
        time_diff = time_calculated - time_scheduled
        print(s, file=sys.stdout)
        print("Scheduled Task (Planzeit):   " + str(time_scheduled) + " : " + scheduled_time.strftime("%H:%M") + str(s.scheduled_time.tzinfo), file=sys.stdout)
        print("Scheduled Task (Startzeit):  " + str(time_calculated) + " : " + s.calculated_time.strftime("%H:%M") + str(s.calculated_time.tzinfo), file=sys.stdout)
        print("Scheduled Task (Verspätung): " + str(time_diff), file=sys.stdout)

        if(time_diff > 1):
            print("Berechne Verspätungen", file=sys.stdout)
            starts = Start.objects.filter(scheduled_time__gt=s.scheduled_time, scheduled_time__year=s.scheduled_time.year, scheduled_time__month=s.scheduled_time.month, scheduled_time__day=s.scheduled_time.day).order_by('scheduled_time')
            for start in starts:
                print("Berechne Verspätung:  " + start.id, file=sys.stdout)
                start.calculated_time = start.scheduled_time.astimezone(timezone(settings.TIME_ZONE)) + timedelta(minutes=time_diff)
                start.save()

    else:
        print("Scheduled Task (Ausgeschaltet)", file=sys.stdout)

def start():
    scheduler.add_job(calculate_start_time, "cron", minute="*/5", id="calculate_start_time", replace_existing=True)

    # Add the scheduled jobs to the Django admin interface
    register_events(scheduler)

    scheduler.start()
    print("Scheduler started...", file=sys.stdout)
