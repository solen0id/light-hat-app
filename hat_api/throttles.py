import time

from django.core.cache import caches
from rest_framework.throttling import SimpleRateThrottle

from emf_hat.settings import TASK_POST_PER_IP_RATE, TASK_VOTE_PER_IP_PER_MINUTE


class IPAddressRateThrottle(SimpleRateThrottle):
    scope = "ip"
    rate = TASK_POST_PER_IP_RATE

    def get_cache_key(self, request, view):
        # Use the user's IP address as the unique identifier
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class TaskIDRateThrottle(SimpleRateThrottle):
    scope = "task_id"
    cache = caches["default"]
    rate = f"{TASK_VOTE_PER_IP_PER_MINUTE}/minute"

    def get_cache_key(self, request, view):
        task_id = view.kwargs.get("pk")
        ip = self.get_ident(request)
        return f"{self.scope}:{ip}:{task_id}"
