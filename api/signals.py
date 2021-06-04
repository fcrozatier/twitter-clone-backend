from django.dispatch import receiver
from graphql_auth.signals import user_registered

from api.models import UserNode


@receiver(user_registered)
def create_user_node(sender, user, **kwargs):
    print("A User has been registered !!!!")
    print(f"User uid {user.uid}")
    user_node = UserNode(uid=user.uid).save()
    print(f"The UserNode has id {user_node.id} and uid {user_node.uid}")
