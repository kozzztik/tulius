from .models import Setting

def get_setting(folder, name, default=None):
    settings = Setting.objects.filter(folder=folder, name=name)
    if settings.count() > 0:
        return settings[0].value
    else:
        return default
    
def set_setting(folder, name, value):
    setting = Setting.objects.get_or_create(folder=folder, name=name)[0]
    setting.value = value
    setting.save()
    