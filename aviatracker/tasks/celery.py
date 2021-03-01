from celery import Celery


app = Celery(
    "tasks",
    broker="pyamqp://guest@localhost//",
    backend="rpc://",
    include=["aviatracker.tasks.tasks"],
)

app.conf.beat_schedule = {
    "every-five-sec-insert-states": {
        "task": "aviatracker.tasks.tasks.insert_states",
        "schedule": 5.0,
        "args": (),
    },
    "every-twenty-sec-update-paths": {
        "task": "aviatracker.tasks.tasks.update_paths",
        "schedule": 20.0,
        "args": (),
    },
    "every-23-hours-update-callsigns": {
        "task": "aviatracker.tasks.tasks.update_callsigns",
        "schedule": 900,
        "args": (),
    },
    "every-hour-update-stats": {
        "task": "aviatracker.tasks.tasks.update_stats",
        "schedule": 3600.0,
        "args": (),
    },
}