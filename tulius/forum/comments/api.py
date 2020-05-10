from djfw.wysibb.templatetags import bbcodes

from tulius.forum import site
from tulius.forum.threads import api
from tulius.forum.comments import pagination


# TODO reply form
# TODO delete form
# TODO dynamic updates button

def comment_to_json(c):
    return {
        'id': c.id,
        'url': c.get_absolute_url,
        'title': c.title,
        'body': bbcodes.bbcode(c.body),
        'user': api.user_to_json(c.user, detailed=True),
        'create_time': c.create_time,
        'voting': c.voting, # TODO voting
        'edit_right': c.edit_right,
        'is_thread': c.is_thread(),
        'is_liked': False, # TODO
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
