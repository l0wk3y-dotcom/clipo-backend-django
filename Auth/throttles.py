from rest_framework.throttling import UserRateThrottle

class OnePerMinuteThrottler(UserRateThrottle):
    rate = "1/minute"