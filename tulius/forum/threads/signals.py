from django import dispatch

# return callable to apply to parent if needed.
# if callable returns callable - it will be applied to parent of parent
# end etc recursively.
# callable have only one parameter - thread. Use object methods or
# functools partial if you need to provide additional params.
on_fix_counters = dispatch.Signal(
    providing_args=['thread' , 'with_descendants', 'view'])
