from django import http
from django import urls
from django.contrib import auth
from django.views import generic
from django.utils import decorators
from django.contrib.auth import decorators as auth_decorators
from ws4redis import redis_store
from websockets import publisher

from .forms import PrivateMessageForm
from .models import PrivateTalking, PrivateMessage


class PlayerMessagesView(generic.TemplateView):
    template_name = 'pm/messages.haml'

    @decorators.method_decorator(auth_decorators.login_required)
    def get(self, *args, **kwargs):
        return super(PlayerMessagesView, self).get(*args, **kwargs)

    @decorators.method_decorator(auth_decorators.login_required)
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['talkings'] = PrivateTalking.objects.filter(
            receiver=self.request.user)[:25]
        return kwargs


class PlayerSendMessageView(generic.DetailView):
    template_name = "pm/to_user.haml"
    queryset = auth.get_user_model().objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        user = self.request.user
        player = self.object
        message_list_tmp = PrivateMessage.objects.talking(user, player)

        unread = PrivateMessage.objects.filter(
            receiver=user, sender=player, is_read=False)
        unread_count = unread.count()
        count = 5
        if unread_count > 5:
            count = unread_count
        message_list_tmp = message_list_tmp.order_by('-id')[:count].all()
        message_list = []
        for message in message_list_tmp:
            message_list = [message] + message_list
        unread.update(is_read=True)
        user.update_not_readed()
        form = PrivateMessageForm(user, player)
        return {
            'player': player,
            'message_list': message_list,
            'form': form,
        }

    @decorators.method_decorator(auth_decorators.login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = PrivateMessageForm(
            request.user, self.object, data=request.POST or None)
        if form.is_valid():
            m = form.save()
            # if the publisher is required only for fetching messages, use an
            # empty constructor, otherwise reuse an existing redis_publisher
            redis_publisher = publisher.RedisPublisher(
                facility='pm', users=[self.object])
            message = redis_store.RedisMessage(str(m.pk))
            # and somewhere else
            redis_publisher.publish_message(message)
        return http.HttpResponseRedirect(
            urls.reverse('pm:to_user', args=(self.object.pk,)))
