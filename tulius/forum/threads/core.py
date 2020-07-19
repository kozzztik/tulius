from django import dispatch

from tulius.forum import plugins


class ThreadsCorePlugin(plugins.ForumPlugin):
    def init_core(self):
        self.thread_on_create = dispatch.Signal(providing_args=['instance'])
        self.signals['thread_on_create'] = self.thread_on_create
