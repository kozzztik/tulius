from django import dispatch


thread_view = dispatch.Signal(providing_args=['response'])

# analyze data and prepare to jsonify
thread_prepare_room = dispatch.Signal(
    providing_args=["room", "threads"])
thread_prepare_threads = dispatch.Signal(providing_args=["threads"])

# prepare data to json
thread_room_to_json = dispatch.Signal(
    providing_args=["thread", "response"])

comment_to_json = dispatch.Signal(
    providing_args=["comment", "data"])

before_add_comment = dispatch.Signal(
    providing_args=["comment", "data", "preview"])
after_add_comment = dispatch.Signal(
    providing_args=["comment", "data", "preview"])
