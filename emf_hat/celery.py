# myproject/celery.py
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emf_hat.settings")

app = Celery("emf_hat")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "run-most-upvoted-task-periodically": {
        "task": "emf_hat.celery.run_most_upvoted_task",
        "schedule": 20.0,
    },
}


@app.task
def run_most_upvoted_task():
    from hat_api.models import HatText
    from hat_api.tasks import run_task

    most_upvoted_task = HatText.objects.order_by("-vote_count").first()

    if most_upvoted_task:
        model_name = most_upvoted_task.__class__.__name__
        run_task.delay(most_upvoted_task.pk, model_name)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
