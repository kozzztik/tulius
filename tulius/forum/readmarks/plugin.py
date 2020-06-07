from django.conf import urls

from tulius.forum import plugins
from tulius.forum.readmarks import views


class ReadMarksPlugin(plugins.ForumPlugin):
    def mark_thread_url(self, thread):
        return self.reverse('mark_as_readed', thread.id)

    def mark_all_url(self):
        return self.reverse('mark_as_readed')

    def mark_as_readed(self, thread, read_mark=None, readed_id=None):
        models = self.site.core.models
        if not thread.last_comment:
            return
        if not read_mark:
            read_marks = models.ThreadReadMark.objects.filter(
                thread=thread, user=thread.view_user)
            if read_marks:
                read_mark = read_marks[0]
            else:
                read_mark = models.ThreadReadMark(
                    thread=thread, user=thread.view_user)
        if readed_id:
            if read_mark.readed_comment_id and (
                    read_mark.readed_comment_id < readed_id):
                read_mark.readed_comment_id = readed_id
            comments = models.Comment.objects.filter(
                parent=thread, id__gt=readed_id, deleted=False
            ).exclude(user=thread.view_user)
            if comments:
                read_mark.not_readed_comment = comments[0]
            else:
                read_mark.not_readed_comment = None
        else:
            read_mark.readed_comment_id = thread.last_comment_id
            read_mark.not_readed_comment = None
        read_mark.save()

    def get_read_mark(self, thread):
        user = thread.view_user
        marks = self.models.ThreadReadMark.objects.filter(
            thread=thread, user=user)
        return marks[0] if marks else None

    def comments_readed(self, sender, **kwargs):
        user = kwargs['user']
        comments = kwargs['comments']
        if not user.is_anonymous:
            last_readed = None
            readmark = sender.get_read_mark
            if readmark:
                last_readed = readmark.readed_comment_id
                if last_readed:
                    for comment in comments:
                        comment.unreaded = (comment.id > last_readed) and (
                            comment.user_id != user.id)
            self.mark_as_readed(sender, readmark)

    def after_add_comment(self, sender, **kwargs):
        restore = kwargs['restore']
        if not restore:
            thread = kwargs['thread']
            self.models.ThreadReadMark.objects.filter(
                thread=thread, not_readed_comment=None
            ).update(not_readed_comment=sender)

    def before_delete_comment(self, sender, **kwargs):
        thread = kwargs['thread']
        if (sender.id != thread.first_comment) and (
                thread.last_comment_id == sender.id):
            comments = self.models.Comment.objects.filter(
                parent=thread, deleted=False).exclude(id=sender.id)
            comments = comments.order_by('-id')
            if comments:
                thread.last_comment_id = comments[0].id
            comments = self.models.Comment.objects.filter(
                parent=thread, deleted=False, id__gt=sender.id).order_by('id')
            read_marks = self.models.ThreadReadMark.objects.filter(
                thread=thread, not_readed_comment=sender.id)
            new_not_readed = comments[0].id if comments else None
            read_marks.update(not_readed_comment=new_not_readed)

    def read_comments_page(self, thread, user, comments):
        unreaded = []
        if not user.is_anonymous:
            last_readed = None
            readmark = thread.get_read_mark
            unreaded_id = None
            if readmark:
                last_readed = readmark.readed_comment_id
                if last_readed:
                    unreaded_id = last_readed
                    for comment in comments:
                        comment.unreaded = (comment.id > last_readed) and (
                            comment.user_id != user.id)
                        if comment.unreaded and comment.id > unreaded_id:
                            unreaded_id = comment.id
                    Comment = self.site.core.models.Comment
                    comments = Comment.objects.filter(
                        parent=thread, pk__gt=last_readed, deleted=False
                    ).exclude(user=user)
                    for comment in comments:
                        unreaded += [(comment.id, comment.page)]
            self.mark_as_readed(thread, readmark, readed_id=unreaded_id)
        return unreaded

    def view_comments_page(self, sender, **kwargs):
        if not sender.room:
            sender.unreaded_comments = self.read_comments_page(
                sender, kwargs['user'], kwargs['comments'])

    def view_comments_page_json(self, sender, **kwargs):
        json = kwargs['json']
        thread = kwargs['thread']
        json['unreaded'] = thread.unreaded_comments

    def init_core(self):
        self.Comment = self.models.Comment
        self.urlizer['Thread_mark_as_readed'] = self.mark_thread_url
        self.urlizer['Thread_get_mark_all_as_readed_url'] = \
            self.mark_thread_url
        self.urlizer['mark_as_readed'] = self.mark_all_url
        self.core['Thread_mark_as_readed'] = self.mark_as_readed
        self.core['Thread_get_read_mark'] = self.get_read_mark
        self.site.signals.after_add_comment.connect(self.after_add_comment)
        self.site.signals.before_delete_comment.connect(
            self.before_delete_comment)
        self.site.signals.read_comments.connect(self.view_comments_page)
        self.site.signals.view_comments_page.connect(
            self.view_comments_page_json)

    def get_urls(self):
        return [
            urls.url(
                r'^mark_all_as_readed/$',
                views.MarkAsRead.as_view(plugin=self),
                name='mark_as_readed'),
            urls.url(
                r'^mark_all_as_readed/(?P<thread_id>\d+)/$',
                views.MarkAsRead.as_view(plugin=self),
                name='mark_as_readed'),
        ]


def room_group_unreaded_url(rooms):
    unreaded = None
    for room in rooms:
        if room.unreaded:
            if (not unreaded) or (room.unreaded_id < unreaded.id):
                unreaded = room.unreaded
    return unreaded.get_absolute_url if unreaded else None
