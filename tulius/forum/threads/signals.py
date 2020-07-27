from django import dispatch

# return callable to apply to parent if needed.
# if callable returns callable - it will be applied to parent of parent
# end etc recursively.
# callable have only one parameter - thread. Use object methods or
# functools partial if you need to provide additional params.
on_fix_counters = dispatch.Signal(
    providing_args=['thread', 'with_descendants', 'view'])

to_json = dispatch.Signal(
    providing_args=['instance', 'response', 'view'])

before_create = dispatch.Signal(providing_args=['instance', 'data', 'view'])
after_create = dispatch.Signal(
    providing_args=['instance', 'data', 'preview', 'view'])
on_update = dispatch.Signal(
    providing_args=['instance', 'data', 'preview', 'view'])

prepare_room = dispatch.Signal(providing_args=['room', 'threads', 'view'])
prepare_threads = dispatch.Signal(providing_args=['threads', 'view'])
room_to_json = dispatch.Signal(providing_args=['instance', 'response', 'view'])
apply_mutation = dispatch.Signal(providing_args=['mutation', 'instance'])
