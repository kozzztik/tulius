from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .forms import PrivateMessageForm
from .models import PrivateTalking, PrivateMessage
from websockets.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage


class PlayerMessagesView(TemplateView):
    template_name='pm/messages.haml'

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(PlayerMessagesView, self).get(*args, **kwargs)

    @method_decorator(login_required)
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['talkings'] = PrivateTalking.objects.filter(receiver=self.request.user)[:25]
        return kwargs


class PlayerSendMessageView(DetailView):
    template_name = "pm/to_user.haml"
    queryset = get_user_model().objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        user = self.request.user
        player = self.object
        message_list_tmp = PrivateMessage.objects.talking(user, player)

        pre_unread_messages = PrivateMessage.objects.filter(receiver=user, is_read=False)
        pre_unread_messages_count = pre_unread_messages.count()

        unread = PrivateMessage.objects.filter(receiver=user, sender=player, is_read=False)
        unread_count = unread.count()
        count = 5
        if unread_count > 5 :
            count = unread_count
        message_list_tmp = message_list_tmp.order_by('-id')[:count].all()
        message_list = []
        for message in message_list_tmp:
            message_list = [message] + message_list
        unread.update(is_read=True)
        user.update_not_readed()
        form = PrivateMessageForm(user, player)
        return locals()

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = PrivateMessageForm(request.user, self.object, data=request.POST or None)
        if form.is_valid():
            m = form.save()
            # if the publisher is required only for fetching messages, use an
            # empty constructor, otherwise reuse an existing redis_publisher
            redis_publisher = RedisPublisher(facility='pm', users=[self.object])
            message = RedisMessage(str(m.pk))
            # and somewhere else
            redis_publisher.publish_message(message)
        return HttpResponseRedirect(reverse('pm:to_user', args=(self.object.pk,)))
