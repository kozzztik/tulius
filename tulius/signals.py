from django import dispatch

user_to_json = dispatch.Signal(
    providing_args=['instance', 'response', 'detailed'])
