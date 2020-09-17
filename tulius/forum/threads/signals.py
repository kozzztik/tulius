from django import dispatch

to_json = dispatch.Signal(
    providing_args=['instance', 'response', 'view'])

before_create = dispatch.Signal(
    providing_args=['instance', 'data', 'view', 'preview'])
after_create = dispatch.Signal(
    providing_args=['instance', 'data', 'preview', 'view'])
on_update = dispatch.Signal(
    providing_args=['instance', 'data', 'preview', 'view'])

prepare_room = dispatch.Signal(
    providing_args=['room', 'threads', 'view', 'response'])
room_to_json = dispatch.Signal(providing_args=['instance', 'response', 'view'])
index_to_json = dispatch.Signal(providing_args=['groups', 'view', 'response'])
apply_mutation = dispatch.Signal(providing_args=['mutation', 'instance'])
