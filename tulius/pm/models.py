from django.db import models
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _

from djfw.common.models import AbstractBaseModel
from tulius.models import User
from tulius.pm.signals import private_message_created


class PrivateMessageManager(models.Manager):
    def talking(self, user_me, user_him):
        query = Q(receiver=user_me, sender=user_him, removed_by_receiver=False)
        query = query | Q(
            receiver=user_him, sender=user_me, removed_by_sender=False)
        return self.filter(query).order_by('-id')


class PrivateMessage(AbstractBaseModel):

    class Meta(AbstractBaseModel.Meta):
        verbose_name = _('private message')
        verbose_name_plural = _('private messages')
        ordering = ['-created_at']
    
    objects = PrivateMessageManager()
    
    sender = models.ForeignKey(
        User, models.PROTECT,
        verbose_name=_('sender'),
        related_name='messages_sent')
    receiver = models.ForeignKey(
        User, models.PROTECT,
        verbose_name=_('receiver'),
        related_name='messages_recieved')

    is_read = models.BooleanField(default=False, verbose_name=_('is read'))
    removed_by_sender = models.BooleanField(
        default=False,
        verbose_name=_('removed by sender'))
    removed_by_receiver = models.BooleanField(
        default=False,
        verbose_name=_('removed by receiver'))
    body = models.TextField(default='', verbose_name=_('message body'))

    def save(self, *args, **kwargs):
        if self.sender_id == self.receiver_id:
            self.is_read = True
        if not self.id:
            super(PrivateMessage, self).save(*args, **kwargs)
            private_message_created.send(sender=self, game=self)
            PrivateTalking.objects.update_talking(
                self.sender, self.receiver, self)
            PrivateTalking.objects.update_talking(
                self.receiver, self.sender, self)
        else:
            super(PrivateMessage, self).save(*args, **kwargs)


class PrivateTalkingManager(models.Manager):
    def get_talking(self, sender, receiver):
        talkings = self.filter(sender=sender, receiver=receiver)
        if talkings.count() > 0:
            return talkings[0]
        else:
            talking = PrivateTalking(sender=sender, receiver=receiver)
            return talking
        
    def update_talking(self, sender, receiver, post):
        talking = self.get_talking(sender, receiver)
        talking.last = post
        talking.save()


class PrivateTalking(models.Model):
    class Meta(AbstractBaseModel.Meta):
        verbose_name = _('private talking')
        verbose_name_plural = _('private talkings')
        ordering = ['last']
    
    objects = PrivateTalkingManager()

    sender = models.ForeignKey(
        User, models.PROTECT,
        verbose_name=_('sender'),
        related_name='talkings_sent')
    receiver = models.ForeignKey(
        User, models.PROTECT,
        verbose_name=_('receiver'),
        related_name='talkings_recieved')

    last = models.ForeignKey(
        PrivateMessage, models.PROTECT,
        verbose_name=_('talking'),
        related_name='talking')
