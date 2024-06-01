from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import render
from .models import HatText
from .serializers import HatTextSerializer

from django.shortcuts import render
from .models import GenericCompletedVotableTask
from django.db.models import F, Q
from collections import Counter
import re
from emf_hat.settings import N_MOST_ITEMS_STATS


def index(request):
    return render(request, "index.html")


def stats(request):
    most_upvoted_tasks = GenericCompletedVotableTask.objects.order_by("-upvotes")[
        :N_MOST_ITEMS_STATS
    ]

    most_controversial_tasks = (
        GenericCompletedVotableTask.objects.annotate(
            total_votes=F("upvotes") + F("downvotes")
        )
        .filter(
            Q(upvotes__gte=F("downvotes") * 0.8) | Q(downvotes__gte=F("upvotes") * 0.8),
            total_votes__gte=5,
            downvotes__gte=1,
            upvotes__gte=1,
        )
        .order_by("-total_votes")[:N_MOST_ITEMS_STATS]
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
