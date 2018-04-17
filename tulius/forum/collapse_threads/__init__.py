from django.conf.urls import url
from tulius.forum.plugins import ForumPlugin
from .views import CollapseThreads


class CollapsingThreadsPlugin(ForumPlugin):
    def get_collapse_url(self, thread):
        return self.reverse('collapse_thread', thread.id)
    
    def thread_view(self, sender, **args):
        user = args['user']
        if user.is_anonymous():
            return
        ThreadCollapseStatus = self.models.ThreadCollapseStatus
        if sender:
            try:
                collapse_data = ThreadCollapseStatus.objects.get(
                    thread=sender, user=user)
                sender.collapse_rooms = collapse_data.collapse_rooms
                sender.collapse_threads = collapse_data.collapse_threads
            except self.models.ThreadCollapseStatus.DoesNotExist:
                sender.collapse_rooms = False
                sender.collapse_threads = False
        else:
            context = args['context']
            groups = context['groups']
            collapses = ThreadCollapseStatus.objects.filter(
                thread__id__in=[thread.id for thread in groups], user=user)
            for group in groups:
                fc = None
                for collapse in collapses:
                    if collapse.thread_id == group.id:
                        fc = collapse
                        break
                group.collapse_rooms = fc.collapse_rooms if fc else False
                group.collapse_threads = fc.collapse_threads if fc else False
                
    def init_core(self):
        super(CollapsingThreadsPlugin, self).init_core()
        self.urlizer['Thread_get_collapse_url'] = self.get_collapse_url
        self.site.signals.thread_view.connect(self.thread_view)
        
    def get_urls(self):
        return [
            url(
                r'^collapse_thread/(?P<parent_id>\d+)/$',
                CollapseThreads.as_view(self),
                name='collapse_thread'),
        ]
