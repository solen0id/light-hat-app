# myapp/models.py
from django.db import models
from django.db.models import JSONField
from django.db import transaction


# create a mixin for all models that can be upvoted and scheduled as tasks
class VoteableTask(models.Model):
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    vote_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

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

    def archive(self, task_data=None):
        with transaction.atomic():
            GenericCompletedVotableTask.objects.create(
                task_data=task_data,
                upvotes=self.upvotes,
                downvotes=self.downvotes,
            )
            self.delete()


class HatText(VoteableTask, models.Model):
    text = models.CharField(max_length=8)

    @property
    def text_for_hat(self):
        # Make uppercase and pad text with spaces to 9 characters
        # so that the HAT can process it correctly
        text = self.text.upper()
        text = text.ljust(9, " ")

        return text

    def archive(self, task_data=None):
        from .serializers import HatTextSerializer

        task_data = HatTextSerializer(self).data
        return super().archive(task_data=task_data)


class GenericCompletedVotableTask(models.Model):
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    task_data = JSONField()
