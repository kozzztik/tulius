import django.dispatch

maintaince_finished = django.dispatch.Signal(providing_args=["worker"])
maintaince_started = django.dispatch.Signal(providing_args=["worker"])