from django.views.generic import TemplateView


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
        from tulius.models import User
        for player in User.objects.all():
            player.update_not_readed()
