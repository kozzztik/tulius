from django import dispatch

before_add = dispatch.Signal(
    providing_args=['comment', 'data', 'preview', 'view'])
after_add = dispatch.Signal(
    providing_args=['comment', 'data', 'preview', 'view'])

on_delete = dispatch.Signal(providing_args=['comment', 'view'])
