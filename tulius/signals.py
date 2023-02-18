from django import dispatch

# providing_args=['instance', 'response', 'detailed']
user_to_json = dispatch.Signal()
