from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers import interval, date
import time

scheduler = BackgroundScheduler()


def tick():
    print("tick")


trigger = interval.IntervalTrigger(seconds=10)

scheduler.add_job(tick, trigger=trigger, id="tick")
scheduler.start()
while 1:
    job = scheduler.get_job("tick")
    print(job)
    print(job.trigger)
    job.reschedule(date.DateTrigger(datetime.now() + timedelta(seconds=2)))
    time.sleep(5)
