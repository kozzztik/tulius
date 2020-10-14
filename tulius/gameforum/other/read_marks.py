from tulius.forum.comments import signals as comment_signals
from tulius.forum.threads import signals as thread_signals
from tulius.forum.read_marks import views
from tulius.forum.read_marks import mutations as marks_mutations

from tulius.gameforum.threads import mutations
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import views as thread_views
from tulius.gameforum.rights import mutations as rights_mutations
from tulius.gameforum.comments import models as comment_models
from tulius.gameforum.other import models as other_models


class ReadmarkAPI(views.ReadmarkAPI, thread_views.BaseThreadAPI):
    read_mark_model = other_models.ThreadReadMark
    comment_model = comment_models.Comment


@mutations.on_mutation(mutations.ThreadCreateMutation)
class ReadmarkOnAddThread(marks_mutations.OnAddThread):
    read_mark_model = other_models.ThreadReadMark


mutations.on_mutation(rights_mutations.UpdateRights)(
    marks_mutations.OnThreadChange)
comment_signals.on_delete.connect(
    ReadmarkAPI.on_delete_comment, sender=comment_models.Comment)
comment_signals.after_add.connect(
    ReadmarkAPI.after_add_comment, sender=comment_models.Comment)
thread_signals.to_json.connect(
    ReadmarkAPI.on_thread_to_json, sender=thread_models.Thread)
