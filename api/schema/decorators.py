# def add_base_resolvers(cls):
#     """
#     For each user defined argument of a class, adds a default resolver to the class returning the parent attribute.
#     """
#     resolvers = {}
#     attrs = cls.__dict__.keys()
#     for attr in attrs:
#         resolver_name = f"resolve_{attr}"
#         # Make a resolver for every non private attribute which doesn't have a custom resolver
#         if not attr.startswith("_") and not attr.startswith("resolve") and resolver_name not in attrs:

#             def make_resolver(attr):
#                 def resolver(parent, info):
#                     return getattr(parent, attr)

#                 return resolver

#             resolvers[resolver_name] = make_resolver(attr)

#     for resolver_name, resolver in resolvers.items():
#         setattr(cls, resolver_name, staticmethod(resolver))
#     return cls
