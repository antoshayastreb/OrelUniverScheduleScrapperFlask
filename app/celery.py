from celery import Celery

app = Celery('proj',
             broker='redis://localhost:6379/0',
             include=['app.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

app.conf.beat_schedule = {
    'add-every-10-seconds': {
        'task': 'app.tasks.add_schedule_periodic',
        'schedule': 10.0
    },
}

app.conf.timezone = 'Europe/Moscow'

if __name__ == '__main__':
    app.start()
