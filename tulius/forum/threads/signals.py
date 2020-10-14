from django import dispatch

to_json = dispatch.Signal(
    providing_args=['instance', 'response', 'user', 'children'])
to_json_as_item = dispatch.Signal(
    providing_args=['instance', 'response', 'user'])

before_create = dispatch.Signal(
    providing_args=['instance', 'data', 'view', 'preview'])
after_create = dispatch.Signal(
    providing_args=['instance', 'data', 'preview', 'view'])
on_update = dispatch.Signal(
    providing_args=['instance', 'data', 'preview', 'view'])

index_to_json = dispatch.Signal(providing_args=['groups', 'view', 'response'])
apply_mutation = dispatch.Signal(providing_args=['mutation', 'instance'])
after_move = dispatch.Signal(providing_args=['instance', 'view', 'old_parent'])
