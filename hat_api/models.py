# myapp/models.py
from django.db import models
from django.db.models import JSONField


# create a mixin for all models that can be upvoted and scheduled as tasks
class VoteableTask(models.Model):
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    vote_count = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def upvote(self):
        self.upvotes += 1
        self.vote_count += 1
        self.save()

    def downvote(self):
        self.downvotes += 1
        self.vote_count -= 1
        self.save()


class HatText(VoteableTask, models.Model):
    text = models.CharField(max_length=8)


class GenericCompletedVotableTask(models.Model):
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    task_data = JSONField()
