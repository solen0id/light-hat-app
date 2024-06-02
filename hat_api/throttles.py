import time

from django.core.cache import caches
from rest_framework.throttling import BaseThrottle, SimpleRateThrottle

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


class TaskIDRateThrottle(BaseThrottle):
    scope = "task_id"
    cache = caches["default"]
    rate = f"{TASK_VOTE_PER_IP_PER_MINUTE}/minute"

    def get_cache_key(self, request, view):
        task_id = view.kwargs.get("task_id")
        ip = self.get_ident(request)
        return f"{self.scope}:{ip}:{task_id}"

    def allow_request(self, request, view):
        cache_key = self.get_cache_key(request, view)
        if not cache_key:
            return True

        # Get the current timestamp
        now = time.time()
        # Get the request history from the cache
        history = self.cache.get(cache_key, [])

        # Drop old entries from the history
        history = [timestamp for timestamp in history if now - timestamp < 3600]

        if len(history) >= TASK_VOTE_PER_IP_PER_MINUTE:
            # Too many requests
            return False

        # Add the current timestamp to the history and update the cache
        history.append(now)
        self.cache.set(cache_key, history, timeout=3600)

        return True

    def wait(self):
        # Optionally implement this method if you want to return the time until the rate limit is reset
        return None
