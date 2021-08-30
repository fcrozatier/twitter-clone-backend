from django.dispatch import receiver
from graphql_auth.signals import user_registered

from api.models.models import UserNode


@receiver(user_registered)
def create_user_node(sender, user, **kwargs):
    UserNode(uid=user.uid).save()
