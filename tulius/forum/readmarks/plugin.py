from tulius.forum import plugins


class ReadMarksPlugin(plugins.ForumPlugin):
    def before_delete_comment(self, sender, **kwargs):
        thread = kwargs['thread']
        if (sender.id != thread.first_comment_id) and (
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

    def init_core(self):
        self.Comment = self.models.Comment
        self.site.signals.before_delete_comment.connect(
            self.before_delete_comment)
