from django.db import models

class VK_Profile(models.Model):
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    nickname = models.CharField(max_length=255, blank=True)
    domain = models.CharField(max_length=255, blank=True)
    vk_id = models.IntegerField(blank=False, null=False, unique=True)
    photo = models.CharField(max_length=255, blank=False)
    sex = models.IntegerField(blank=False, null=False, default=0)
    access_token = models.CharField(max_length=255, blank=True, default='')
    token_expires = models.DateTimeField(blank=True, null=True)