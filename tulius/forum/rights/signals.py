from django import dispatch

after_update = dispatch.Signal(providing_args=['instance', 'view'])
