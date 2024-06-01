from rest_framework import serializers

from .models import HatText, VoteableTask


class VoteableTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteableTask
        fields = "__all__"


class HatTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = HatText
        fields = "__all__"

    # do a custom method for the field "text" where we check a condition
