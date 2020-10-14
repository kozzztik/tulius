from django import dispatch

to_json = dispatch.Signal(
    providing_args=['instance', 'response', 'user', 'children'])
to_json_as_item = dispatch.Signal(
    providing_args=['instance', 'response', 'user'])

before_create = dispatch.Signal(
    providing_args=['instance', 'data', 'user', 'preview'])
after_create = dispatch.Signal(
    providing_args=['instance', 'data', 'preview', 'user'])
on_update = dispatch.Signal(
    providing_args=['instance', 'data', 'preview', 'user'])

index_to_json = dispatch.Signal(providing_args=['groups', 'user', 'response'])
apply_mutation = dispatch.Signal(providing_args=['mutation', 'instance'])
after_move = dispatch.Signal(providing_args=['instance', 'user', 'old_parent'])
