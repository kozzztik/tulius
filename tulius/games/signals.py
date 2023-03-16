import django.dispatch

# providing_args=['old_status', 'new_status']
game_status_changed = django.dispatch.Signal()

# providing_args=['instance', 'new_status']
role_assign_changed = django.dispatch.Signal()
