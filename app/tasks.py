import celery
from routes import Exercise


@celery.Task(bind=True)
def add_schedule_events(self, schedule_exercises):
    pass
