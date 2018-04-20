from django.apps import apps
from django.views.generic import TemplateView

site = apps.get_app_config('forum').site


class CountersIndex(TemplateView):
    template_name = 'counters/index.haml'


class CountersBase(TemplateView):
    template_name = 'counters/success.haml'
    
    def do_action(self):
        raise NotImplemented()
    
    def get_context_data(self, **kwargs):
        self.do_action()
        return super(CountersBase, self).get_context_data(**kwargs)


class ForumNums(CountersBase):
    def do_action(self):
        site = apps.get_app_config('forum').site
        site.core.rebuild_tree(None)


class PMCounters(CountersBase):
    def do_action(self):
        from tulius.models import User
        for player in User.objects.all():
            player.update_not_readed()
