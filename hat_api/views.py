from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import render
from .models import HatText
from .serializers import HatTextSerializer

from django.shortcuts import render
from .models import GenericCompletedVotableTask
from django.db.models import F, Q


def index(request):
    return render(request, "index.html")


def stats(request):
    most_upvoted_tasks = GenericCompletedVotableTask.objects.order_by("-upvotes")[:10]

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
        .order_by("-total_votes")[:10]
    )

    context = {
        "most_upvoted_tasks": most_upvoted_tasks,
        "most_controversial_tasks": most_controversial_tasks,
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
