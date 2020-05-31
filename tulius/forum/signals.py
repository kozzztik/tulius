from django import dispatch


thread_view = dispatch.Signal(providing_args=['response'])
thread_prepare_room = dispatch.Signal(
    providing_args=["room", "threads"])
thread_prepare_threads = dispatch.Signal(providing_args=["threads"])
