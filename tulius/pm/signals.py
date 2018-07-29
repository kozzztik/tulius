from django import dispatch

private_message_created = dispatch.Signal(providing_args=[])
