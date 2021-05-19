from neomodel import DateTimeProperty, StringProperty, StructuredNode, UniqueIdProperty


class User(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)


class Post(StructuredNode):
    uid = UniqueIdProperty()
    content = StringProperty(required=True)
    created = DateTimeProperty(default_now=True)
