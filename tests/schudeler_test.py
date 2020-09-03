from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers import interval, date
import time

scheduler = BackgroundScheduler()


def tick():
    print("tick")
    job.reschedule(date.DateTrigger(datetime.now() + timedelta(seconds=2)))


trigger = interval.IntervalTrigger(seconds=10)

scheduler.add_job(tick, trigger=trigger, id="tick")
scheduler.start()
while 1:
    job = scheduler.get_job("tick")
    print(job)
    print(job.trigger)
    print(job.next_run_time)
    time.sleep(5)
