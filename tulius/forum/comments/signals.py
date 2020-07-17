from django import dispatch


on_delete = dispatch.Signal(providing_args=["comment", "view"])
