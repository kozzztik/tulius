from django.http import Http404
from .plugin import BasePluginView

class RebuildNums(BasePluginView):
    template_name = 'fixes'
    
    def get_context_data(self, post_id=None, **kwargs):
        thread = self.core.models.Thread
        if not self.request.user.is_superuser:
            raise Http404
        if post_id:
            thread.objects.get(id=post_id).rebuild
        else:
            parent_post = None
            self.core.rebuild_tree(parent_post)
        return BasePluginView.get_context_data(self, **kwargs)

class FixLastPost(BasePluginView):
    template_name = 'fixes'
    
    def get_context_data(self, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404
        models = self.core.models
        threads = models.Thread.objects.all()
        for thread in threads:
            comment = models.Comment.objects.filter(parent=thread).order_by('-id')[:1]
            if comment:
                models.Thread.objects.filter(id=thread.id).update(last_comment=comment[0].id)
        return BasePluginView.get_context_data(self, **kwargs)
    
class FixHtml(BasePluginView):
    template_name = 'fixes'
    
    def get_context_data(self, **kwargs):

        fix_expr = [
            (r'<p (.*?)>', r''),
            ]
        import re
        import gc
        import logging
        models = self.core.models
        logger = logging.getLogger('django.request')
        logger.error("Started forum fixing html")
        def do_fix_comment(comment):
            value = comment.body
    
            for expr in fix_expr:
                p = re.compile(expr[0], re.DOTALL)
                value = p.sub(expr[1], value)
            
            comment.body = value
            
        def scan_threads(parent_thread):
            threads = models.Thread.objects.filter(parent=parent_thread).order_by('id')
            for thread in threads:
                if not parent_thread:
                    logger.error("Fixing thread %s" % (thread.id,))
                if thread.room:
                    scan_threads(thread)
                else:
                    comments = models.Comment.objects.filter(parent=thread)
                    for comment in comments:
                        do_fix_comment(comment)
                        comment.save()
                        if comment.num == 1:
                            thread.body = comment.body[:255]
                            thread.save()
                if not parent_thread:
                    gc.collect()
        scan_threads(None)
        logger.error("forum fixing html done.")
        return BasePluginView.get_context_data(self, **kwargs)