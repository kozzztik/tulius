from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import PrivateTalking


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
