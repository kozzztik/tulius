from django.views.generic import TemplateView

from tulius import models


class CountersIndex(TemplateView):
    template_name = 'counters/index.haml'


class CountersBase(TemplateView):
    template_name = 'counters/success.haml'

    def do_action(self):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        self.do_action()
        return super().get_context_data(**kwargs)


class PMCounters(CountersBase):
    def do_action(self):
        for player in models.User.objects.all():
            player.update_not_readed()
