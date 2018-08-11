from django.conf.urls import url
from django.db.models.query_utils import Q
from django.http import Http404
# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin, BasePluginView
from tulius.stories.models import Role
from tulius.games.models import Game
from .views import GameIndex, VariationIndex, Fix
from .forms import EditorForm, RoleForm


class GamePlugin(ForumPlugin):

    def game_url(self, game):
        return self.reverse('game', game.id)

    def variation_url(self, variation):
        return self.reverse('variation', variation.id)

    def copy_game_post(self, thread, new_parent, variation, rolelinks):
        models = self.site.models
        gamemodels = self.site.gamemodels
        subthreads = models.Thread.objects.filter(parent=thread, deleted=False)
        rights = gamemodels.GameThreadRight.objects.filter(thread=thread)
        old_thread = thread
        thread = models.Thread(
            title=old_thread.title, parent=new_parent,
            body=old_thread.body, room=old_thread.room, user=old_thread.user,
            access_type=old_thread.access_type,
            create_time=old_thread.create_time, closed=old_thread.closed,
            important=old_thread.important, plugin_id=self.site_id)
        role_id = old_thread.data1
        if role_id and (role_id in rolelinks):
            thread.data1 = rolelinks[role_id].id
        thread.save()
        if not new_parent:
            variation.thread = thread
            variation.save()
        thread.variation = variation
        for right in rights:
            right.id = None
            right.thread = thread
            if right.role_id and (right.role_id in rolelinks):
                right.role = rolelinks[right.role_id]
            right.save()
        for subpost in subthreads:
            self.copy_game_post(subpost, thread, variation, rolelinks)

        if not old_thread.room:
            first_comment = None
            subcomments = models.Comment.objects.filter(
                parent=old_thread, deleted=False)
            for comment in subcomments:
                new_comment = models.Comment(
                    parent=thread, title=comment.title, body=comment.body,
                    plugin_id=self.site_id,
                    user=comment.user, create_time=comment.create_time,
                    voting=comment.voting)
                new_comment.reply_id = first_comment
                if comment.data1 and (comment.data1 in rolelinks):
                    new_comment.data1 = rolelinks[comment.data1].id
                new_comment.save()
                if not first_comment:
                    first_comment = new_comment.id
        return thread

    def create_gameforum(self, user, variation):
        models = self.site.models
        if variation.game:
            title = variation.game.name
        else:
            title = variation.name
        thread = models.Thread(
            title=title, user=user,
            access_type=models.THREAD_ACCESS_TYPE_OPEN,
            room=True, plugin_id=self.site_id)
        thread.save()
        return thread

    def copy_game_forum(self, variation, rolelinks, user):
        if not variation.thread:
            variation.thread = self.create_gameforum(user, variation)
            variation.save()
        thread = self.copy_game_post(
            variation.thread, None, variation, rolelinks)
        thread.title = variation.game.name
        thread.save()
        return thread

    def get_role(self, role_id, roles, admin):
        if role_id == '':
            if admin:
                return None
            raise Http404()
        for role in roles:
            if int(role.id) == int(role_id):
                return role
        raise Http404()

    # pylint: disable=too-many-branches
    def process_role(
            self, request, parent_thread, init_role_id, new=False, user=None):
        if not user:
            user = request.user
        variation = parent_thread.variation
        admin = parent_thread.admin
        init_role = None
        if init_role_id:
            init_role = Role.objects.get(id=init_role_id)
        form = None
        if variation.game:
            query = Q(variation=variation)
            if not admin:
                query = query & Q(user=user)
            roles = Role.objects.filter(query).exclude(deleted=True)
            roles = [role for role in roles]
            strict_write = parent_thread.strict_write
            if strict_write is not None:
                roles = [role for role in roles if role in strict_write]
            if not new:
                post_role = init_role
                role_found = False
                for form_role in roles:
                    if post_role == form_role:
                        role_found = True
                if not role_found:
                    roles += [post_role]
        else:
            roles = Role.objects.filter(
                variation=variation).exclude(deleted=True)
        role = None
        if (roles.count == 0) and (not admin):
            raise Http404()
        if len(roles) == 1:
            role = roles[0]
            form = None
        else:
            if new:
                init_role = None
                for tmp_role in roles:
                    if tmp_role.user_id == user.id:
                        init_role = tmp_role
                        break
        if (len(roles) > 1) or admin:
            if init_role:
                init_role = init_role.pk
            form = RoleForm(
                admin, roles,
                data=(request.POST or None) if request else None,
                initial={'role': init_role})
            if request and (request.method == 'POST'):
                if not form.is_valid():
                    raise Http404(form.errors)
                cd = form.cleaned_data
                role_id = cd['role']
                role = self.get_role(role_id, roles, admin)
        return form, role

    def process_editor(self, request, parent_thread, comment):
        variation = parent_thread.variation
        admin = parent_thread.admin
        init_editor = comment.data2 if comment else None
        form = None
        query = Q(variation=variation)
        if not admin:
            query = query & Q(user=request.user)
        roles = Role.objects.filter(query)
        roles = [role for role in roles]
        if parent_thread.strict_write:
            strict_ids = [role.id for role in parent_thread.strict_write]
            roles = [role for role in roles if role.id in strict_ids]
        editor = None
        if (roles.count == 0) and (not admin):
            raise Http404()
        if len(roles) == 1:
            editor = roles[0]
            form = None
        if (len(roles) > 1) or admin:
            form = EditorForm(
                admin, roles, data=request.POST or None,
                initial={'editor': init_editor})
            if request.method == 'POST':
                if not form.is_valid():
                    raise Http404(form.errors)
                cd = form.cleaned_data
                role_id = cd['editor']
                editor = self.get_role(role_id, roles, admin)
        return (form, editor)

    def thread_view(self, sender, **kwargs):
        context = kwargs['context']
        variation = sender.variation
        context['variation'] = variation
        if sender.write_right():
            (roleform, role) = self.process_role(
                None, sender, None, True, user=sender.view_user)
            context['roleform'] = roleform
            context['role'] = role

    def thread_before_edit(self, sender, **kwargs):
        if sender.self_is_room:
            return

    def thread_after_edit(self, sender, **kwargs):
        if sender.self_is_room:
            return
        context = kwargs['context']
        thread = kwargs['thread']
        comment = sender.comment
        parent_thread = sender.parent_thread
        init_role_id = comment.data1 if comment else None
        (roleform, role) = self.process_role(
            sender.request, parent_thread, init_role_id, sender.adding)
        editor = None
        if parent_thread.game and not sender.adding:
            (editorform, editor) = self.process_editor(
                sender.request, parent_thread, comment)
            context['editorform'] = editorform
            context['editor'] = editor
        context['roleform'] = roleform
        context['role'] = role
        if thread and comment:
            if role:
                self.models.Thread.objects.filter(
                    id=thread.id).update(data1=role.id)
                comment.data1 = role.id
            if editor:
                comment.data2 = editor.id
            comment.save()

    def comment_before_fast_reply(self, sender, **kwargs):
        context = kwargs['context']
        (roleform, role) = self.process_role(
            sender.request, sender.parent_thread, None, True)
        context['roleform'] = roleform
        context['role'] = role
        sender.role = role

    def comment_after_fast_reply(self, sender, **kwargs):
        comment = sender.comment
        role = sender.role
        if comment:
            if role:
                comment.data1 = role.id
            comment.save()

    def comment_before_edit(self, sender, **kwargs):
        comment = kwargs['comment']
        sender.init_role_id = comment.data1 if comment else None

    def comment_after_edit(self, sender, **kwargs):
        context = kwargs['context']
        adding = kwargs['adding']
        comment = sender.comment
        parent_thread = sender.parent_thread
        (roleform, role) = self.process_role(
            sender.request, parent_thread, sender.init_role_id, adding)
        context['roleform'] = roleform
        context['role'] = role
        editor = None
        if parent_thread.game and (not adding):
            (editorform, editor) = self.process_editor(
                sender.request, parent_thread, comment)
            context['editorform'] = editorform
            context['editor'] = editor
        if comment:
            if role:
                comment.data1 = role.id
            if editor:
                comment.data2 = editor.id
            comment.save()

    def fix_games(self):
        games = Game.objects.all()
        for game in games:
            variation = game.variation
            root_thread = variation.thread
            if not root_thread:
                continue
            tree_id = root_thread.tree_id
            roles = Role.objects.filter(variation=variation)
            for role in roles:
                comments = self.models.Comment.objects.filter(
                    parent__tree_id=tree_id, deleted=False, data1=role.id)
                role.comments_count = comments.count()
                role.save()
            variation.comments_count = self.models.Comment.objects.filter(
                parent__tree_id=tree_id, deleted=False).count()
            variation.save()

    def init_core(self):
        super(GamePlugin, self).init_core()
        self.urlizer['game'] = self.game_url
        self.urlizer['variation'] = self.variation_url
        self.core['copy_game_forum'] = self.copy_game_forum
        self.core['create_gameforum'] = self.create_gameforum
        self.core['fix_games'] = self.fix_games
        self.templates['fix_games'] = 'gameforum/fix.haml'
        self.site.signals.thread_view.connect(self.thread_view)
        self.site.signals.thread_before_edit.connect(self.thread_before_edit)
        self.site.signals.thread_after_edit.connect(self.thread_after_edit)
        self.site.signals.comment_before_fastreply.connect(
            self.comment_before_fast_reply)
        self.site.signals.comment_after_fastreply.connect(
            self.comment_after_fast_reply)
        self.site.signals.comment_before_edit.connect(self.comment_before_edit)
        self.site.signals.comment_after_edit.connect(self.comment_after_edit)

    def get_urls(self):
        return [
            url(
                r'^game/(?P<game_id>\d+)/$',
                GameIndex.as_view(plugin=self),
                name='game'),
            url(
                r'^variation/(?P<variation_id>\d+)/$',
                VariationIndex.as_view(plugin=self),
                name='variation'),
            url(
                r'^fix/$',
                Fix.as_view(plugin=self),
                name='fix'),
        ]
