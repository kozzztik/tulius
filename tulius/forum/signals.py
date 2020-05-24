from django import dispatch


thread_view = dispatch.Signal(providing_args=['response'])
