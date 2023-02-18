from django import dispatch

# providing_args=['comment', 'data', 'preview', 'user']
before_add = dispatch.Signal()

# returning result on "after add" that is bool(result) == True will make
# comment save again. So you do not need to re-save comment changes in signal
# receivers
# providing_args=['comment', 'data', 'preview', 'user']
after_add = dispatch.Signal()
# providing_args=['comment', 'user']
on_delete = dispatch.Signal()
# providing_args=['instance', 'mutation']
on_thread_delete = dispatch.Signal()
# providing_args=['comment', 'data', 'preview', 'user']
on_update = dispatch.Signal()

# providing_args=['comment', 'data', 'user']
to_json = dispatch.Signal()
