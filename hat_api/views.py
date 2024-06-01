from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import render
from .models import HatText
from .serializers import HatTextSerializer

from django.shortcuts import render


def index(request):
    return render(request, "index.html")


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
