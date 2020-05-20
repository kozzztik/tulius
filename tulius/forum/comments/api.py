import json

from django import shortcuts
from django.core import exceptions
from django.utils import html
from djfw.wysibb.templatetags import bbcodes

from tulius.core.ckeditor import html_converter
from tulius.forum import site
from tulius.forum import models
from tulius.forum.threads import api
from tulius.forum.comments import pagination


# TODO unreaded messages
# TODO dynamic updates button
# TODO cancel error in sentry

def comment_to_json(c):
    return {
        'id': c.id,
        'url': c.get_absolute_url,
        'title': html.escape(c.title),
        'body': bbcodes.bbcode(c.body),
        'user': api.user_to_json(c.user, detailed=True),
        'create_time': c.create_time,
        'voting': c.voting,
        'edit_right': c.edit_right,
        'is_thread': c.is_thread(),
        'edit_time': c.edit_time,
        'editor': api.user_to_json(c.editor) if c.editor else None
    }


class CommentsPageAPI(api.BaseThreadView):
    def get_context_data(self, **kwargs):
        super(CommentsPageAPI, self).get_context_data(**kwargs)
        page_num = int(kwargs['page_num'])
        comments = site.site.core.get_comments_page(
            self.user, self.obj, page_num)
        pagination_context = pagination.get_pagination_context(
            self.request, page_num, self.obj.pages_count)
        return {
            'pagination': pagination_context,
            'comments': [comment_to_json(c) for c in comments]
        }

    def post(self, *args, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.obj.write_right(self.user):
            raise exceptions.PermissionDenied()
        data = json.loads(self.request.body)
        text = html_converter.html_to_bb(data['body'])
        reply_id = data['reply_id']
        if reply_id != self.obj.first_comment_id:
            obj = shortcuts.get_object_or_404(models.Comment, pk=reply_id)
            if obj.parent_id != self.obj.id:
                raise exceptions.PermissionDenied()
        preview = data.get('preview', False)
        if text:
            comment = models.Comment(plugin_id=self.obj.plugin_id)
            comment.parent = self.obj
            comment.user = self.user
            comment.title = "Re: " + self.obj.title
            comment.body = text
            comment.reply_id = reply_id
            if preview:
                return comment_to_json(comment)
            comment.save()
            site.site.signals.comment_after_fastreply.send(self)
            page = comment.page
        else:
            page = self.obj.pages_count
        return self.get_context_data(page_num=page, **kwargs)
