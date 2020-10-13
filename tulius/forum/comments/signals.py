from django import dispatch

before_add = dispatch.Signal(
    providing_args=['comment', 'data', 'preview', 'view'])

# returning result on "after add" that is bool(result) == True will make
# comment save again. So you do not need to re-save comment changes in signal
# receivers
after_add = dispatch.Signal(
    providing_args=['comment', 'data', 'preview', 'view'])

on_delete = dispatch.Signal(providing_args=['comment', 'view'])
on_thread_delete = dispatch.Signal(providing_args=['instance', 'mutation'])
on_update = dispatch.Signal(
    providing_args=['comment', 'data', 'preview', 'view'])

to_json = dispatch.Signal(providing_args=['comment', 'data', 'user'])
