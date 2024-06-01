from django.contrib import admin

from .models import HatText, GenericCompletedVotableTask

# Register your models here.
admin.site.register(HatText)
admin.site.register(GenericCompletedVotableTask)
