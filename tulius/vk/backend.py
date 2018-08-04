from django.contrib.auth.backends import ModelBackend
from django.core.files.base import ContentFile
from tulius.models import User, USER_SEX_FEMALE, USER_SEX_MALE, \
    USER_SEX_UNDEFINED


class VKBackend(ModelBackend):
    def check_name(self, name):
        try:
            User.objects.get(username=name)
            return False
        except User.DoesNotExist:
            return True

    def get_valid_name(self, profile):
        names = [
            profile.nickname,
            '%s_%s' % (profile.first_name, profile.last_name)
        ]
        names += [
            '%s_%s_%s' % (
                profile.first_name, profile.nickname, profile.last_name)]
        names += ['vk_' + str(profile.vk_id)]
        for name in names:
            new_name = name.replace(' ', '_')
            if new_name and self.check_name(new_name):
                return new_name
        raise ValueError()

    def register_user(self, profile, email):
        user = User(vk_profile=profile, email=email)
        if profile.sex == 1:
            user.sex = USER_SEX_FEMALE
        elif profile.sex == 2:
            user.sex = USER_SEX_MALE
        else:
            user.sex = USER_SEX_UNDEFINED
        user.username = self.get_valid_name(profile)
        import urllib
        data = urllib.urlopen(profile.photo)
        img = ContentFile(data.read())
        user.avatar.save('vk_' + str(profile.vk_id), img, False)
        user.save()
        return user

    def authenticate(self, vk_profile=None, email=None):
        try:
            return User.objects.get(vk_profile_id=vk_profile.pk)
        except User.DoesNotExist:
            if email:
                users = User.objects.filter(email=email)
                if users:
                    user = users[0]
                    user.vk_profile = vk_profile
                    user.save()
                    return user
                return self.register_user(vk_profile, email)
