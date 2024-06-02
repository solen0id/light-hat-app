from rest_framework import serializers

from .models import HatText, VoteableTask, HatActivity


class VoteableTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteableTask
        fields = "__all__"


class HatTextSerializer(serializers.ModelSerializer):
    is_ready = serializers.SerializerMethodField()

    class Meta:
        model = HatText
        fields = "__all__"

    def get_is_ready(self, obj):
        return bool(obj.is_ready) if hasattr(obj, "is_ready") else None

    # do a custom method for the field "text" where we check a condition


class HatActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HatActivity
        fields = "__all__"
