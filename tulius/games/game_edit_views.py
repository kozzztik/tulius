from django import http
from django import shortcuts
from django import urls
from django.contrib import messages
from django.views import generic
from django.contrib.auth import decorators
from django.utils.translation import ugettext_lazy as _

from djfw import custom_views
from djfw import subviews
from djfw import inlineformsets
from djfw import uploader
from djfw import views as djfw_views
from djfw.sortable import views as sortable_views

from tulius.core import autocomplete
from tulius.stories import models as stories_models
from tulius.stories import edit_variation_forms as variation_forms
from tulius.stories import materials_forms

from tulius.games import game_edit_forms
from tulius.games import game_edit_catalog
from tulius.games import views
from tulius.games import forms
from tulius.games import models


class GameAdminViewMixin(sortable_views.DecoratorChainingMixin):
    model = models.Game
    context_object_name = 'game'
    pk_url_kwarg = 'game_id'
    decorators = [decorators.login_required]
    page_url = None
    paging_class = game_edit_catalog.EditGamePage

    def get_object(self, *args, **kwargs):
        game = super(GameAdminViewMixin, self).get_object(*args, **kwargs)
        self.variation = game.variation
        if not game.edit_right(self.request.user):
            raise http.Http404()
        gamepage = self.paging_class(game)
        self.catalog_page = gamepage.get_subpage(
            urls.reverse(
                game_edit_catalog.URL_PREFIX + self.page_url, args=(game.pk,)))
        return game

    def get_context_data(self, **kwargs):
        context = super(GameAdminViewMixin, self).get_context_data(**kwargs)
        context['catalog_page'] = self.catalog_page
        return context


class GameAdminView(GameAdminViewMixin, generic.DetailView):
    pass


class GameEditFormView(GameAdminViewMixin, generic.UpdateView):
    def get_success_url(self):
        messages.success(self.request, _('game was successfully updated'))
        return self.object.get_edit_url()

    def form_invalid(self, form):
        messages.error(
            self.request, _('there were some errors during form validation'))
        return super(GameAdminMain, self).form_invalid(form)


class GameAdminMain(GameEditFormView):
    template_name = 'base_cataloged_navig_form_game.haml'
    page_url = game_edit_catalog.EDIT_GAME_PAGES_MAIN
    form_class = game_edit_forms.EditGameMainForm


class GameAdminTexts(GameEditFormView):
    template_name = 'stories/edit_story/texts.haml'
    page_url = game_edit_catalog.EDIT_GAME_PAGES_TEXTS
    form_class = game_edit_forms.EditGameTextsForm


class GameAdminUsers(custom_views.ActionableViewMixin, GameAdminView):
    template_name = 'games/game_edit/users.haml'
    page_url = game_edit_catalog.EDIT_GAME_PAGES_USERS
    widgets = {
        'game_admins': {
            'class': custom_views.FormsetWidget,
            'model': models.GameAdmin,
            'table_class': 'table'},
        'game_guests': {
            'class': custom_views.FormsetWidget,
            'model': models.GameGuest,
            'table_class': 'table'}}


class GraphicFile:
    def __init__(self, game, name):
        self.name = name
        field = None
        for i in game._meta.fields:
            if i.name == name:
                field = i
                break
        self.caption = field.verbose_name
        field = getattr(game, name)
        self.saved = field.name != ''
        self.url = field.url if self.saved else ''


GRAPHIC_FIELDS = ['card_image', 'top_banner', 'bottom_banner']


class GameAdminGraphics(GameAdminView):
    template_name = 'games/game_edit/graphics.haml'
    page_url = game_edit_catalog.EDIT_GAME_PAGES_GRAPHICS

    def get_context_data(self, **kwargs):
        context = super(GameAdminGraphics, self).get_context_data(**kwargs)
        context['game_files'] = [
            GraphicFile(self.object, name) for name in GRAPHIC_FIELDS]
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        field_name = request.GET['field_name']
        if field_name in GRAPHIC_FIELDS:
            field = getattr(obj, field_name)
        else:
            raise http.Http404()
        return uploader.handle_field_upload(
            request, field, '%s.jpg' % (obj.pk,))


class GameEditRoles(GameAdminView, sortable_views.SortableDetailViewMixin):
    template_name = 'games/game_edit/roles.haml'
    sortable_key = "role_"
    sortable_field = 'order'
    sortable_model = models.Role
    page_url = game_edit_catalog.EDIT_GAME_PAGES_ROLES

    def get_sortable_queryset(self):
        game = self.get_object()
        return models.Role.objects.filter(
            variation_id=game.variation_id).exclude(deleted=True)

    def get_context_data(self, **kwargs):
        context = super(GameEditRoles, self).get_context_data(**kwargs)
        roles = self.get_sortable_queryset()
        for role in roles:
            role.invitings = models.GameInvite.objects.filter(
                role=role, status=models.GAME_INVITE_STATUS_NEW)
        context['roles'] = roles
        context['inviteform'] = forms.GameInviteForm(variation=self.variation)
        context['delete_role_form'] = variation_forms.RoleDeleteForm(
            self.variation)
        return context


class EditRoleMixin(djfw_views.RightsDetailMixin):
    form_class = variation_forms.RoleForm
    model = models.Role
    catalog_page_name = ''
    catalog_page_url = game_edit_catalog.EDIT_GAME_PAGES_ROLES
    success_message = _('role was successfully updated')
    template_name = 'base_cataloged_navig_form.haml'

    def get_form_kwargs(self):
        kwargs = super(EditRoleMixin, self).get_form_kwargs()
        if self.form_class == variation_forms.RoleForm:
            if self.object:
                kwargs['story'] = self.object.variation.story
            else:
                kwargs['story'] = self.parent_object.variation.story
        return kwargs

    def get_success_url(self):
        return urls.reverse(
            'games:edit_game_roles', args=(self.object.variation.game_id,))

    def get_context_data(self, **kwargs):
        game = self.game if self.object else self.parent_object
        kwargs['catalog_page'] = game_edit_catalog.CatalogPage(
            name=self.catalog_page_name,
            instance=self.object,
            parent=game_edit_catalog.EditGameSubpage(
                game, url=self.catalog_page_url))
        kwargs['game'] = game
        if not self.object:
            kwargs['form_submit_title'] = _("add")
        return super(EditRoleMixin, self).get_context_data(**kwargs)

    def check_rights(self, obj, user):
        self.game = obj.variation.game
        return self.game.edit_right(user)


class AddRoleView(EditRoleMixin, views.MessageMixin, subviews.SubCreateView):
    parent_model = models.Game
    parent_obj_foreign_key = 'dummy'
    catalog_page_name = _('Add role')
    success_message = _('role was successfully added')

    def get_parent_object(self, queryset=None):
        obj = super(AddRoleView, self).get_parent_object()
        if not obj.edit_right(self.request.user):
            raise http.Http404()
        return obj

    def form_valid(self, form):
        role = form.save(commit=False)
        role.variation = self.parent_object.variation
        role.save()
        messages.success(self.request, self.success_message)
        return http.HttpResponseRedirect(
            urls.reverse(
                'games:' + self.catalog_page_url,
                args=(self.parent_object.id,)))


class AddMaterialView(AddRoleView):
    model = stories_models.AdditionalMaterial
    catalog_page_name = ('Add material')
    catalog_page_url = game_edit_catalog.EDIT_GAME_PAGES_MATERIALS
    success_message = _('Additional material was successfully added')
    form_class = materials_forms.AdditionalMaterialForm


class GameEditRoleView(EditRoleMixin, views.MessageMixin, generic.UpdateView):
    pass


class GameRoleTextView(EditRoleMixin, views.MessageMixin, generic.UpdateView):
    template_name = 'stories/variation/role_text.haml'
    form_class = variation_forms.RoleTextForm
    catalog_page_name = _('text')


class EditRoleAssignView(djfw_views.RightsDetailMixin, generic.DetailView):
    template_name = 'games/game_edit/role_assign.haml'
    model = models.Role

    def check_rights(self, obj, user):
        self.game = obj.variation.game
        return self.game.edit_right(user)

    def get_context_data(self, **kwargs):
        kwargs['game'] = self.game
        parent_page = game_edit_catalog.CatalogPage(
            instance=self.object,
            parent=game_edit_catalog.EditGameSubpage(
                self.game, url=game_edit_catalog.EDIT_GAME_PAGES_ROLES))
        kwargs['catalog_page'] = game_edit_catalog.CatalogPage(
            name=_('user'), parent=parent_page)
        requests = models.RoleRequest.objects.filter(game=self.game)
        for role_request in requests:
            role_request.new_games = calc_games(
                role_request.user,
                [
                    models.GAME_STATUS_NEW,
                    models.GAME_STATUS_OPEN_FOR_REGISTRATION,
                    models.GAME_STATUS_REGISTRATION_COMPLETED
                ])
            role_request.current_games = calc_games(
                role_request.user, [models.GAME_STATUS_IN_PROGRESS])
            role_request.complited_games = calc_games(
                role_request.user,
                [
                    models.GAME_STATUS_COMPLETED,
                    models.GAME_STATUS_COMPLETED_OPEN
                ])
            role_request.roles = models.RoleRequestSelection.objects.filter(
                role_request=role_request)
            role_request.assigned = models.Role.objects.filter(
                variation=self.game.variation, user=role_request.user)
        kwargs['requests'] = requests
        return super(EditRoleAssignView, self).get_context_data(**kwargs)


class BaseGameDetailView(djfw_views.RightsDetailMixin, generic.DetailView):
    model = models.Game

    def check_rights(self, obj, user):
        return obj.edit_right(user)


class GameEditIllustrationsView(BaseGameDetailView):
    template_name = 'stories/materials/illustrations.haml'

    def get_context_data(self, **kwargs):
        kwargs['catalog_page'] = game_edit_catalog.EditGameSubpage(
            self.object, url=game_edit_catalog.EDIT_GAME_PAGES_ILLUSTRATIONS)
        variation = self.object.variation
        kwargs['variation'] = variation
        kwargs['story'] = variation.story
        kwargs['illustrations'] = stories_models.Illustration.objects.filter(
            variation=variation)
        return super(GameEditIllustrationsView, self).get_context_data(
            **kwargs)


class GameEditMaterialsView(BaseGameDetailView):
    template_name = 'stories/materials/materials.haml'

    def get_context_data(self, **kwargs):
        kwargs['catalog_page'] = game_edit_catalog.EditGameSubpage(
            self.object, url=game_edit_catalog.EDIT_GAME_PAGES_MATERIALS)
        variation = self.object.variation
        kwargs['variation'] = variation
        kwargs['story'] = variation.story
        kwargs['materials'] = stories_models.AdditionalMaterial.objects.filter(
            variation=variation)
        return super(GameEditMaterialsView, self).get_context_data(**kwargs)


class BaseDeleteMaterialView(
        djfw_views.RightsDetailMixin, generic.edit.BaseDeleteView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def check_rights(self, obj, user):
        self.variation = obj.variation
        if (not self.variation) or (not self.variation.game):
            return False
        return obj.edit_right(user)


class DeleteIllustration(BaseDeleteMaterialView):
    model = stories_models.Illustration

    def get_success_url(self):
        return urls.reverse(
            'games:' + game_edit_catalog.EDIT_GAME_PAGES_ILLUSTRATIONS,
            args=(self.variation.game.pk,))


class DeleteMaterial(BaseDeleteMaterialView):
    model = stories_models.AdditionalMaterial

    def get_success_url(self):
        return urls.reverse(
            'games:' + game_edit_catalog.EDIT_GAME_PAGES_MATERIALS,
            args=(self.variation.game.pk,))


class BaseEditMaterialView(
        djfw_views.RightsDetailMixin, views.MessageMixin, generic.UpdateView):
    login_required = True
    parent_page_url = game_edit_catalog.EDIT_GAME_PAGES_MATERIALS

    def check_rights(self, obj, user):
        self.variation = obj.variation
        if (not self.variation) or (not self.variation.game):
            return False
        return obj.edit_right(user)

    def get_context_data(self, **kwargs):
        kwargs['catalog_page'] = game_edit_catalog.CatalogPage(
            name=self.object,
            parent=game_edit_catalog.EditGameSubpage(
                self.variation.game, url=self.parent_page_url))
        kwargs['variation'] = self.variation
        kwargs['story'] = self.variation.story
        kwargs['materials'] = stories_models.AdditionalMaterial.objects.filter(
            variation=self.variation)
        return super(BaseEditMaterialView, self).get_context_data(**kwargs)

    def get_success_url(self):
        return urls.reverse(
            'games:' + self.parent_page_url, args=(self.variation.game.pk,))


class EditIllustrationView(BaseEditMaterialView):
    template_name = 'stories/materials/illustration.haml'
    parent_page_url = game_edit_catalog.EDIT_GAME_PAGES_ILLUSTRATIONS
    model = stories_models.Illustration
    form_class = materials_forms.IllustrationForm
    success_message = _('Illustration was successfully updated')


class EditMaterialView(BaseEditMaterialView):
    template_name = 'stories/materials/material.haml'
    model = stories_models.AdditionalMaterial
    form_class = materials_forms.AdditionalMaterialForm
    success_message = _('Additional material was successfully updated')


class MaterialView(djfw_views.RightsDetailMixin, generic.DetailView):
    template_name = 'stories/material.haml'
    model = stories_models.AdditionalMaterial
    context_object_name = 'material'

    def check_rights(self, obj, user):
        self.variation = obj.variation
        if (not self.variation) or (not self.variation.game):
            return False
        if obj.admins_only and (not obj.edit_right(user)):
            raise http.Http404()
        return True

    def get_context_data(self, **kwargs):
        parent = game_edit_catalog.CatalogPage(
            instance=self.variation.game,
            parent=game_edit_catalog.games_catalog_page(),
            is_index=True)
        kwargs['catalog_page'] = game_edit_catalog.CatalogPage(
            instance=self.object, parent=parent)
        kwargs['parent'] = parent
        return super(MaterialView, self).get_context_data(**kwargs)


def calc_games(user, status):
    variation_ids = [
        role['variation'] for role in
        models.Role.objects.filter(user=user).values('variation').distinct()]
    variations = stories_models.Variation.objects.filter(
        id__in=variation_ids, game__status__in=status)
    return variations.count()


class BaseEditGameView(djfw_views.RightsDetailMixin, generic.DetailView):
    model = models.Game

    def check_rights(self, obj, user):
        return obj.edit_right(user)


class EditRequestsView(BaseEditGameView):
    template_name = 'games/game_edit/requests.haml'

    def get_context_data(self, **kwargs):
        game = self.object
        catalog_page = game_edit_catalog.EditGameSubpage(
            game, url=game_edit_catalog.EDIT_GAME_PAGES_REQUESTS)
        requests = models.RoleRequest.objects.filter(game=game)
        assigned_users = game.get_assigned_users()
        requests = requests.exclude(user__in=assigned_users)
        assigned_roles = models.Role.objects.filter(user__isnull=False)
        all_roles = models.Role.objects.filter(
            variation=game.variation, requestable=True, user__isnull=True)
        for role_request in requests:
            role_request.new_games = calc_games(
                role_request.user,
                [
                    models.GAME_STATUS_NEW,
                    models.GAME_STATUS_OPEN_FOR_REGISTRATION,
                    models.GAME_STATUS_REGISTRATION_COMPLETED
                ])
            role_request.current_games = calc_games(
                role_request.user, [models.GAME_STATUS_IN_PROGRESS])
            role_request.complited_games = calc_games(
                role_request.user,
                [
                    models.GAME_STATUS_COMPLETED,
                    models.GAME_STATUS_COMPLETED_OPEN
                ])
            role_request.roles = models.RoleRequestSelection.objects.filter(
                role_request=role_request).exclude(role__in=assigned_roles)
        return {
            'catalog_page': catalog_page,
            'requests': requests,
            'all_roles': all_roles,
        }


class GameForumView(BaseEditGameView):
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        return http.HttpResponseRedirect(
            urls.reverse('gameforum:game', args=(obj.pk,)))


class BaseGameFormsetView(
        djfw_views.RightsDetailMixin, views.MessageMixin, generic.UpdateView):
    model = models.Game
    template_name = 'games/game_edit/winners.haml'

    def get_form(self, form_class=None):
        return inlineformsets.get_formset(
            models.Game, self.form_model, self.request.POST, self.form_class,
            extra=1, instance=self.object, params={'game': self.object})

    def get_context_data(self, **kwargs):
        kwargs['formset'] = kwargs.pop('form')
        kwargs['catalog_page'] = game_edit_catalog.EditGameSubpage(
            self.object, url=self.catalog_url)
        return super(BaseGameFormsetView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.save()
        return http.HttpResponseRedirect(
            urls.reverse('games:' + self.catalog_url, args=(self.object.pk,)))


class EditRequestView(BaseGameFormsetView):
    form_class = game_edit_forms.GameRequestQuestionForm
    form_model = models.RequestQuestion
    catalog_url = game_edit_catalog.EDIT_GAME_PAGES_REQUEST_FORM
    success_message = _('requests form was successfully updated')


class EditWinnersView(BaseGameFormsetView):
    form_class = game_edit_forms.GameWinnerForm
    form_model = models.GameWinner
    catalog_url = game_edit_catalog.EDIT_GAME_PAGES_WINNERS
    success_message = _('game was successfully updated')


def get_game(user, game_id):
    try:
        game_id = int(game_id)
    except:
        raise http.Http404()
    game = shortcuts.get_object_or_404(models.Game, id=game_id)
    if not game.edit_right(user):
        raise http.Http404()
    return game


@autocomplete.autocomplete_result
@decorators.login_required
def game_edit_players(request, name, limit, game_id):
    game = get_game(request.user, game_id)
    users = game.get_assigned_users()
    user_ids = [user.id for user in users]
    return models.User.objects.filter(
        username__istartswith=name, id__in=user_ids)[:limit]
