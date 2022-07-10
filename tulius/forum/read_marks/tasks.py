from celery import shared_task
from django.apps import apps


def update_read_marks_on_rights_async(thread, only_users=None):
    update_read_marks_on_rights.apply_async(
        args=[
            thread._meta.app_label, thread._meta.object_name, thread.pk,
            only_users])


@shared_task(track_started=True)
def update_read_marks_on_rights(
        app_name, model_name, thread_id, only_users=None):
    thread_cls = apps.get_model(app_name, model_name)
    thread = thread_cls.objects.get(pk=thread_id)
    read_marks = thread.read_marks.select_related('user')
    if only_users:
        read_marks = read_marks.filter(user_id__in=only_users)
    children = thread.children.filter(deleted=False)
    changed_users = []
    for mark in read_marks.iterator(1000):
        threads = [t for t in children if t.read_right(mark.user)]
        user_marks = mark.__class__.objects.filter(
            user=mark.user, thread__in=threads)
        user_marks = {m.thread_id: m for m in user_marks}
        old_not_read = mark.not_read_comment_id
        mark.not_read_comment_id = None
        for child in threads:
            thread_mark = user_marks.get(child.pk)
            if thread_mark:
                not_read = thread_mark.not_read_comment_id
            else:
                not_read = child.first_comment[mark.user]
            if not_read and (
                    (not mark.not_read_comment_id) or (
                        mark.not_read_comment_id > not_read)):
                mark.not_read_comment_id = not_read
        if old_not_read != mark.not_read_comment_id:
            mark.save()
            changed_users.append(mark.user_id)
    if thread.parent_id and changed_users:
        update_read_marks_on_rights.apply_async(
            args=[app_name, model_name, thread.parent_id, changed_users])


def after_thread_move_async(thread):
    update_read_marks_on_move.apply_async(
        args=[thread._meta.app_label, thread._meta.object_name, thread.pk])


@shared_task(track_started=True)
def update_read_marks_on_move(app_name, model_name, thread_id):
    thread_cls = apps.get_model(app_name, model_name)
    thread = thread_cls.objects.get(pk=thread_id)
    read_marks = thread.read_marks.select_related('user')
    changed_users = []
    for mark in read_marks.iterator(1000):
        fixed = False
        for parent_id in reversed(thread.parents_ids):
            parent_mark = mark.__class__.objects.filter(
                user=mark.user, thread_id=parent_id).first()
            if not parent_mark:
                fixed = True
                parent_mark = mark.__class__(
                    user=mark.user, thread=thread.parent,
                    not_read_comment_id=mark.not_read_comment_id)
                parent_mark.save()
            else:
                break
        if fixed:
            changed_users.append(mark.user_id)
    if thread.parent_id and changed_users:
        update_read_marks_on_rights.apply_async(
            args=[app_name, model_name, thread.parent_id, changed_users])
