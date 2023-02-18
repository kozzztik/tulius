from django import forms
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse

from djfw.cataloging.core import CatalogPage
from djfw.inlineformsets import get_formset
from tulius.models import User
from tulius.games.models import GameInvite, GAME_INVITE_STATUS_OCCUPIED
from tulius.stories.models import Role
from .models import Game, RoleRequest, RoleRequestSelection, \
    RequestQuestion, RequestQuestionAnswer
from .catalog import games_catalog_page
from .game_edit_catalog import EDIT_GAME_PAGES_REQUESTS, \
    EDIT_GAME_PAGES_ROLES, EditGameSubpage


def get_game(user, game_id, requested):
    try:
        game_id = int(game_id)
    except ValueError as exc:
        raise Http404() from exc
    game = get_object_or_404(Game, id=game_id)
    if user.is_anonymous:
        raise Http404()
    requests = RoleRequest.objects.filter(game=game, user=user)
    if requested != (requests.count() > 0):
        raise Http404()
    return game, CatalogPage(instance=game, parent=games_catalog_page())


class RoleRequestForm(forms.models.ModelForm):
    class Meta:
        model = RoleRequest
        fields = ('body',)


class RequestAnswerForm(forms.models.ModelForm):
    class Meta:
        model = RequestQuestionAnswer
        fields = ('answer', )

    use_required_attribute = False
    empty_permitted = True

    def after_constuct(self, formset, params, i):
        questions = params['questions']
        if i is not None:
            self.question_text = questions[i]


class RequestSelectionForm(forms.models.ModelForm):
    class Meta:
        model = RoleRequestSelection
        exclude = ('prefer_order',)

    use_required_attribute = False
    empty_permitted = True

    def after_constuct(self, formset, params, i):
        game = params['game']
        self.fields['role'].queryset = self.fields['role'].queryset.filter(
            variation=game.variation, requestable=True
        ).exclude(deleted=True)


@login_required
def make_game_request(
        request, game_id, template_name='games/game_request.haml'):
    """
    Making game request view
    """
    (game, game_page) = get_game(request.user, game_id, False)
    catalog_page = CatalogPage(name=_('make request'), parent=game_page)
    form = RoleRequestForm(data=request.POST or None)
    questions = RequestQuestion.objects.filter(game=game)
    # answers_Formset = get_request_answer_formset(extra=questions.count(),
    # can_delete=False)
    answersformset = get_formset(
        RoleRequest, RequestQuestionAnswer, request.POST, RequestAnswerForm,
        static=True, extra=len(questions),
        params={'game': game, 'questions': questions})
    selectionformset = get_formset(
        RoleRequest, RoleRequestSelection, request.POST, RequestSelectionForm,
        extra=3, params={'game': game})
    if request.method == 'POST':
        # custom validation
        all_valid = True
        for answer_form in answersformset:
            if answer_form.is_valid():
                answer = answer_form.save(commit=False)
                if answer.answer == '':
                    answer_form.my_errors = _('You must answer on question')
                    all_valid = False
        rolelist = []
        if selectionformset.is_valid():
            for sel_form in selectionformset:
                if sel_form.is_valid():
                    selection = sel_form.save(commit=False)
                    try:
                        role = selection.role
                        rolelist.append(role)
                    except:
                        pass
        else:
            all_valid = False
        if form.is_valid() and all_valid:
            # additional validation
            role_request = form.save(commit=False)
            role_request.game = game
            role_request.user = request.user
            role_request.save()
            for form in answersformset:
                answer = form.save(commit=False)
                answer.role_request = role_request
                answer.question = form.question_text
                answer.save()
            for role in rolelist:
                selection = RoleRequestSelection(
                    role_request=role_request, prefer_order=0, role=role)
                selection.save()
            messages.success(
                request, _('Game request was successfully created'))
            return HttpResponseRedirect(catalog_page.parent.parent.url)
        messages.error(
            request, _('there were some errors during form validation'))
    return TemplateResponse(request, template_name, locals())


@login_required
def cancel_game_request(
        request, game_id, template_name='games/game_request.haml'):
    """
    Making game request view
    """
    (game, game_page) = get_game(request.user, game_id, True)
    role_requests = RoleRequest.objects.filter(game=game, user=request.user)
    for role_request in role_requests:
        RoleRequestSelection.objects.filter(role_request=role_request).delete()
        RequestQuestionAnswer.objects.filter(
            role_request=role_request).delete()
        roles = Role.objects.filter(
            variation=game.variation, user=request.user)
        for role in roles:
            role.user = None
            role.save()
        role_request.delete()
    return HttpResponseRedirect(game_page.parent.url)


@login_required
def role_assign_user(request, role_id, user_id, backtoroles=False):
    """
    Assigning user to a role
    """
    try:
        role_id = int(role_id)
        user_id = int(user_id)
    except ValueError as exc:
        raise Http404() from exc
    role = get_object_or_404(Role, id=role_id, deleted=False)
    user = get_object_or_404(User, id=user_id)
    if not role.variation.game:
        raise Http404()
    if not role.variation.edit_right(request.user):
        raise Http404()
    role.user = user
    role.save()
    GameInvite.objects.filter(role=role).update(
        status=GAME_INVITE_STATUS_OCCUPIED)
    if backtoroles:
        back = EDIT_GAME_PAGES_ROLES
    else:
        back = EDIT_GAME_PAGES_REQUESTS
    return HttpResponseRedirect(
        EditGameSubpage(role.variation.game, url=back).url)


@login_required
def role_clear_user(request, role_id):
    """
    Assigning user to a role
    """
    try:
        role_id = int(role_id)
    except ValueError as exc:
        raise Http404() from exc
    role = get_object_or_404(Role, id=role_id)
    if not role.variation.game:
        raise Http404()
    if not role.variation.edit_right(request.user):
        raise Http404()
    role.user = None
    role.save()
    return HttpResponseRedirect(
        EditGameSubpage(role.variation.game, url=EDIT_GAME_PAGES_ROLES).url)
