from .models import Subscription


class IsSubscribedMixin:
    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=user, subscribed_to=obj
            ).exists()
        return False
