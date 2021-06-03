from api.models import UserNode
from django.dispatch import receiver
from graphql_auth.signals import user_registered


@receiver(user_registered)
def create_user_node(sender, user, **kwargs):
    print("A User has been registered !!!!")
    print(f"User id {user.id}")
    UserNode(uid=user.id).save()
