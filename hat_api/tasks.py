# tasks.py
from celery import shared_task
from django.apps import apps
from django.db import transaction
import requests

from .models import GenericCompletedVotableTask, HatText, VoteableTask
from emf_hat.settings import HAT_CONTROLLER_TEXT_ADDRESS


@shared_task
def run_task(task_pk: int, model_name: str):
    try:
        print(f"Running task: {model_name}: {task_pk}")
        Model = apps.get_model(app_label="hat_api", model_name=model_name)
        task = Model.objects.get(id=task_pk)

        # TODO: Add hat connection here

        if isinstance(task, HatText):
            text = task.text_for_hat

            # make post request to HAT Controller
            requests.post(
                HAT_CONTROLLER_TEXT_ADDRESS,
                data=text,
                headers={"Content-Type": "text/plain"},
            )
    except Model.DoesNotExist:
        print(f"Task with id {task_pk} does not exist.")

    finally:

        task_data = {
            "model_name": model_name,
            "task_pk": task_pk,
        }

        if isinstance(task, VoteableTask):
            task_data = {
                **task_data,
                "upvotes": task.upvotes,
                "downvotes": task.downvotes,
            }

        if isinstance(task, HatText):
            task_data = {**task_data, "text": task.text}

        # move to completed tasks and delete from original table
        task.archive(task_data=task_data)
