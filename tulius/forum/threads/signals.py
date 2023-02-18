from django import dispatch

# providing_args=['instance', 'response', 'user', 'children']
to_json = dispatch.Signal()
# providing_args=['instance', 'response', 'user']
to_json_as_item = dispatch.Signal()

# providing_args=['instance', 'data', 'user', 'preview']
before_create = dispatch.Signal()
# providing_args=['instance', 'data', 'preview', 'user']
after_create = dispatch.Signal()
# providing_args=['instance', 'data', 'preview', 'user']
on_update = dispatch.Signal()

# providing_args=['groups', 'user', 'response']
index_to_json = dispatch.Signal()
# providing_args=['mutation', 'instance']
apply_mutation = dispatch.Signal()
# providing_args=['instance', 'user', 'old_parent']
after_move = dispatch.Signal()
