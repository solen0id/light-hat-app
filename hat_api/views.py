from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.decorators import throttle_classes
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render
from django.utils import timezone
from django.db.models import F, Q

from datetime import timedelta
import re
from collections import Counter

from emf_hat.settings import (
    N_MOST_ITEMS_STATS,
    MIN_VOTE_COUNT_FOR_HAT_TASKS,
    MIN_SECONDS_FOR_HAT_TASKS,
)


from .models import HatText
from .models import ApiRequestTimestamp
from .models import GenericCompletedVotableTask

from .serializers import HatTextSerializer, GenericCompletedVotableTaskSerializer

from .throttles import IPAddressRateThrottle, TaskIDRateThrottle



def index(request):
    return render(request, "index.html")


def stats(request):
    most_upvoted_tasks = GenericCompletedVotableTask.objects.order_by("-upvotes")[
        :N_MOST_ITEMS_STATS
    ]

    # controversial tasks meet the following criteria:
    # upvotes to downvote ratio close to one
    # the more total votes the better
    # at least one upvote and one downvote

    most_controversial_tasks = (
        GenericCompletedVotableTask.objects.annotate(
            ratio=F("upvotes") / F("downvotes") + 0.000001,
            vote_count=F("upvotes") + F("downvotes"),
        )
        .filter(
            Q(vote_count__gt=1)
            & Q(upvotes__gt=0)
            & Q(downvotes__gt=0)
            & Q(ratio__lte=1.1)
            & Q(ratio__gte=0.9)
        )
        .order_by("-vote_count")[:N_MOST_ITEMS_STATS]
    )

    # Extract words from task_data['text'] and count occurrences
    word_counter = Counter()
    tasks = GenericCompletedVotableTask.objects.all()

    for task in tasks:
        text = task.task_data.get("text", "")
        words = re.findall(r"\b\w+\b", text.lower())
        word_counter.update(words)

    most_common_words = word_counter.most_common(N_MOST_ITEMS_STATS)

    context = {
        "most_upvoted_tasks": most_upvoted_tasks,
        "most_controversial_tasks": most_controversial_tasks,
        "most_common_words": most_common_words,
    }
    return render(request, "stats.html", context)


class HatTextViewSet(viewsets.ModelViewSet):
    queryset = HatText.objects.all()
    serializer_class = HatTextSerializer
    
    def get_throttles(self):
        if self.request.method == "POST":
            # if its upvote or downvote task, apply TaskIDRateThrottle
            if "upvote" in self.request.path or "downvote" in self.request.path:
                return [TaskIDRateThrottle()]
            # otherwise its a post request to create a task
            return [IPAddressRateThrottle()]

        return super().get_throttles()

    def list(self, request, *args, **kwargs):
        # Custom logic here
        queryset = self.filter_queryset(self.get_queryset())

        # annotate queryset
        now = timezone.now()
        queryset = queryset.annotate(
            is_ready=(
                Q(created_at__lte=now - timedelta(seconds=MIN_SECONDS_FOR_HAT_TASKS))
                | Q(vote_count__gte=MIN_VOTE_COUNT_FOR_HAT_TASKS)
                | Q(text__startswith="!")
            )
        )

        # You can apply pagination if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def upvote(self, request, pk=None):
        task = self.get_object()
        task.upvote()
        return Response(
            {
                "status": "success",
                "upvotes": task.upvotes,
                "downvotes": task.downvotes,
                "vote_count": task.vote_count,
            }
        )

    @action(detail=True, methods=["post"])
    def downvote(self, request, pk=None):
        task = self.get_object()
        task.downvote()
        return Response(
            {
                "status": "success",
                "upvotes": task.upvotes,
                "downvotes": task.downvotes,
                "vote_count": task.vote_count,
            }
        )

    @action(detail=False, methods=["get"], url_path="top-text", url_name="top-text")
    def top_text(self, request):
        # intended only for HAT Controller,
        # thats why it returns text/plain and empty string if no tasks
        top_tasks = HatText.objects.order_by("-vote_count")

        # filter so that we only offer tasks to the hat that are:
        # either more than 60 seconds old
        # or have a vote_count of minimum 10 or more
        # or start with the char ! (for special tasks)

        now = timezone.now()
        
        # remember the time of the request to track the activity of the hat
        ApiRequestTimestamp.objects.update_or_create(id=1, defaults={'timestamp': now})

        top_tasks = top_tasks.filter(
            Q(created_at__lte=now - timedelta(seconds=MIN_SECONDS_FOR_HAT_TASKS))
            | Q(vote_count__gte=MIN_VOTE_COUNT_FOR_HAT_TASKS)
            | Q(text__startswith="!")
        )

        top_task = top_tasks.first()

        if top_task:
            text = top_task.text_for_hat

            if text.startswith("!"):
                text = text[1:]

            top_task.archive()
            return HttpResponse(text)
        else:
            return HttpResponse("")

    # time when the last hat text was requested
    @action(detail=False, methods=["get"], url_path="top-text-requested-time", url_name="top-text-requested-time")
    def top_text_requested(self, request):
        try:
            timestamp_entry = ApiRequestTimestamp.objects.get(id=1)
            return Response({'timestamp': timestamp_entry.timestamp}, status=status.HTTP_200_OK)
        except ApiRequestTimestamp.DoesNotExist:
            return Response({'error': 'Timestamp not found'}, status=status.HTTP_404_NOT_FOUND)
            


class GenericCompletedVotableTaskListView(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = GenericCompletedVotableTask.objects.all()
    serializer_class = GenericCompletedVotableTaskSerializer

    @action(detail=False, methods=["get"], url_path="most-recent", url_name="most-recent")
    def most_recent(self, request):
        obj = self.get_queryset().order_by("-completed_at").first()
        serializer = self.get_serializer(obj, many=False)
        return Response(serializer.data)
