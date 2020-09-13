from django import shortcuts
from django import http
from django import urls
from django.contrib import messages
from django.views import generic
from django.contrib.auth import decorators
from django.utils.translation import gettext_lazy as _

from djfw import custom_views
from djfw import subviews
from djfw import inlineformsets
from djfw import uploader
from djfw import views as djfw_views
from djfw.sortable import views as sortable_views

from tulius.games import views as games_views
from tulius.stories import edit_story_cataloging as story_catalog
from tulius.stories import edit_variation_catalog as variation_catalog
from tulius.stories import materials_forms
from tulius.stories import materials_views
from tulius.stories import models
from tulius.stories import story_edit_forms
from tulius.gameforum import core as game_forum_core


class StoryAdminMixin(djfw_views.RightsDetailMixin):
    model = models.Story
    page_url = None
    success_message = _('story was successfully updated')

    def check_rights(self, obj, user):
        return obj.edit_right(user)

    def get_context_data(self, **kwargs):
        if self.page_url:
            kwargs['catalog_page'] = story_catalog.EditStorySubpage(
                self.object, url=self.page_url)
        return super(StoryAdminMixin, self).get_context_data(**kwargs)

    def get_success_url(self):
        return urls.reverse('stories:' + self.page_url, args=(self.object.pk,))


class StoryMainView(
        StoryAdminMixin, games_views.MessageMixin, generic.UpdateView):
    template_name = 'base_cataloged_navig_form_game.haml'
    form_class = story_edit_forms.EditStoryMainForm
    page_url = story_catalog.EDIT_STORY_PAGES_MAIN


class StoryTextsView(
        StoryAdminMixin, games_views.MessageMixin, generic.UpdateView):
    template_name = 'stories/edit_story/texts.haml'
    form_class = story_edit_forms.EditStoryTextsForm
    page_url = story_catalog.EDIT_STORY_PAGES_TEXTS


class StoryFile:
    name = ''
    caption = ''
    url = ''
    saved = False

    def __init__(self, story, name, caption, field):
        self.name = name
        self.caption = caption
        self.saved = field.name != ''
        if self.saved:
            self.url = field.url
        else:
            self.url = ''


class StoryGraphics(StoryAdminMixin, generic.DetailView):
    template_name = 'stories/edit_story/graphics.haml'
    page_url = story_catalog.EDIT_STORY_PAGES_GRAPHICS

    def get_context_data(self, **kwargs):
        kwargs['story_files'] = (
            StoryFile(
                self.object, 'card_image', _('card image'),
                self.object.card_image),
            StoryFile(
                self.object, 'top_banner', _('top banner'),
                self.object.top_banner),
            StoryFile(
                self.object, 'bottom_banner', _('bottom banner'),
                self.object.bottom_banner),
        )
        return super(StoryGraphics, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        story = self.get_object()
        field_name = request.GET['story_name']
        if field_name == 'card_image':
            field = story.card_image
        elif field_name == 'top_banner':
            field = story.top_banner
        elif field_name == 'bottom_banner':
            field = story.bottom_banner
        else:
            raise http.Http404()
        return uploader.handle_field_upload(
            request, field, '%s.jpg' % (story.pk,))


class UsersFormsets:
    def __init__(
            self, data=None, instance=None, initial=None, static=True,
            **kwargs):
        self.authorformset = inlineformsets.get_formset(
            models.Story, models.StoryAuthor, data,
            story_edit_forms.StoryAuthorForm,
            extra=1, static=static, instance=instance,
            params={'static': static})
        self.adminformset = inlineformsets.get_formset(
            models.Story, models.StoryAdmin, data,
            story_edit_forms.StoryAdminForm,
            extra=1, static=static,
            instance=instance, params={'static': static})
        self.static = static
        self.instance = instance

    def is_valid(self):
        return (
            (not self.static) and self.authorformset.is_valid() and
            self.adminformset.is_valid())

    def save(self):
        self.authorformset.save()
        self.adminformset.save()
        return self.instance


class StoryUsers(
        custom_views.ActionableViewMixin, StoryAdminMixin, generic.DetailView):
    template_name = 'stories/edit_story/users.haml'
    page_url = story_catalog.EDIT_STORY_PAGES_USERS

    def get_editable(self):
        return self.request.user.is_superuser

    widgets = {
        'authorformset': {
            'class': custom_views.FormsetWidget,
            'form_class': story_edit_forms.StoryAuthorForm,
            'model': models.StoryAuthor,
            'table_class': 'table', 'editable': get_editable},
        'adminformset': {
            'class': custom_views.FormsetWidget,
            'form_class': story_edit_forms.StoryAdminForm,
            'model': models.StoryAdmin,
            'table_class': 'table', 'editable': get_editable}
    }


class EditStoryVariations(
        StoryAdminMixin, sortable_views.SortableDetailViewMixin,
        generic.DetailView):
    template_name = 'stories/edit_story/variations.haml'
    sortable_key = "var_"
    sortable_field = 'order'
    sortable_model = models.Variation
    page_url = story_catalog.EDIT_STORY_PAGES_VARIATIONS


class BaseStoryAddView(
        StoryAdminMixin, games_views.MessageMixin, subviews.SubCreateView):
    parent_model = models.Story

    def check_parent_rights(self, obj, user):
        return self.check_rights(obj, user)

    def get_context_data(self, **kwargs):
        kwargs['form_submit_title'] = _("add")
        kwargs['catalog_page'] = story_catalog.CatalogPage(
            name=self.page_name,
            parent=story_catalog.EditStorySubpage(
                self.parent_object, url=self.parent_page_url))
        return super(BaseStoryAddView, self).get_context_data(**kwargs)


class AddVariationView(BaseStoryAddView):
    template_name = 'stories/edit_story/add_variation.haml'
    form_class = story_edit_forms.VariationForm
    parent_page_url = story_catalog.EDIT_STORY_PAGES_VARIATIONS
    page_name = _('Add new variation')
    model = models.Variation

    def form_valid(self, form):
        variation = form.save(commit=False)
        variation.story = self.parent_object
        variation.save()
        variation.thread = game_forum_core.create_game_forum(
            self.request.user, variation)
        variation.save()
        characters = models.Character.objects.filter(story=self.parent_object)
        for character in characters:
            role = models.Role(variation=variation, character=character)
            role.avatar = character.avatar
            role.name = character.name
            role.description = character.description
            role.show_in_character_list = character.show_in_character_list
            role.save()
        messages.success(
            self.request, _('variation was successfully added'))
        return http.HttpResponseRedirect(variation.get_absolute_url())


class EditStoryCharacters(
        StoryAdminMixin, sortable_views.SortableDetailViewMixin,
        generic.DetailView):
    template_name = 'stories/edit_story/characters.haml'
    sortable_key = "char_"
    sortable_field = 'order'
    sortable_model = models.Character
    page_url = story_catalog.EDIT_STORY_PAGES_CHARACTERS


class CharacterFormMixin:
    parent_page_url = story_catalog.EDIT_STORY_PAGES_CHARACTERS

    def get_form_kwargs(self):
        kwargs = super(CharacterFormMixin, self).get_form_kwargs()
        kwargs['story'] = self.parent_object
        return kwargs

    def get_success_url(self):
        return urls.reverse(
            'stories:' + self.parent_page_url, args=(self.parent_object.pk,))


class AddCharacterView(CharacterFormMixin, BaseStoryAddView):
    template_name = 'base_cataloged_navig_form_game.haml'
    form_class = story_edit_forms.CharacterForm
    model = models.Character
    page_name = _('Add new character')
    success_message = _('character was successfully added')


class CharacterView(
        CharacterFormMixin, djfw_views.RightsDetailMixin,
        games_views.MessageMixin, generic.UpdateView):
    template_name = 'base_cataloged_navig_form_game.haml'
    model = models.Character
    form_class = story_edit_forms.CharacterForm
    success_message = _('character was successfully updated')

    def check_rights(self, obj, user):
        self.parent_object = obj.story
        return self.parent_object.edit_right(user)

    def get_context_data(self, **kwargs):
        kwargs['story'] = self.parent_object
        kwargs['catalog_page'] = story_catalog.CatalogPage(
            name=self.object,
            parent=story_catalog.EditStorySubpage(
                self.parent_object, url=self.parent_page_url))
        return super(CharacterView, self).get_context_data(**kwargs)


class StoryAvatarsView(StoryAdminMixin, generic.DetailView):
    template_name = 'stories/edit_story/avatars.haml'
    page_url = story_catalog.EDIT_STORY_PAGES_AVATARS


class StoryIllustrationsView(StoryAdminMixin, generic.DetailView):
    template_name = 'stories/materials/illustrations.haml'
    page_url = story_catalog.EDIT_STORY_PAGES_ILLUSTRATIONS

    def get_context_data(self, **kwargs):
        kwargs['illustrations'] = models.Illustration.objects.filter(
            story=self.object)
        return super(StoryIllustrationsView, self).get_context_data(**kwargs)


class StoryMaterialsView(StoryAdminMixin, generic.DetailView):
    template_name = 'stories/materials/materials.haml'
    page_url = story_catalog.EDIT_STORY_PAGES_MATERIALS

    def get_context_data(self, **kwargs):
        kwargs['materials'] = models.AdditionalMaterial.objects.filter(
            story=self.object)
        return super(StoryMaterialsView, self).get_context_data(**kwargs)


class StoryDeleteAvatarView(
        djfw_views.RightsDetailMixin, generic.edit.BaseDeleteView):
    model = models.Avatar

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def check_rights(self, obj, user):
        self.story = obj.story
        return obj.story.edit_right(user)

    def get_success_url(self):
        return urls.reverse(
            'stories:' + story_catalog.EDIT_STORY_PAGES_AVATARS,
            args=(self.story.pk,))


class EditAvatarView(
        djfw_views.RightsDetailMixin, games_views.MessageMixin,
        generic.UpdateView):
    template_name = 'stories/edit_story/avatar.haml'
    model = models.Avatar
    form_class = story_edit_forms.AvatarForm
    success_message = _('avatar was successfully updated')
    parent_page_url = story_catalog.EDIT_STORY_PAGES_AVATARS

    def check_rights(self, obj, user):
        self.story = obj.story
        return obj.story.edit_right(user)

    def get_context_data(self, **kwargs):
        kwargs['story'] = self.story
        kwargs['catalog_page'] = story_catalog.CatalogPage(
            name=self.object,
            parent=story_catalog.EditStorySubpage(
                self.story, url=self.parent_page_url))
        return super(EditAvatarView, self).get_context_data(**kwargs)

    def get_success_url(self):
        return urls.reverse('stories:' + self.parent_page_url, args=(
            self.story.pk,))


class EditIllustrationView(
        djfw_views.RightsDetailMixin, games_views.MessageMixin,
        generic.UpdateView):
    template_name = 'stories/materials/illustration.haml'
    model = models.Illustration
    form_class = materials_forms.IllustrationForm
    success_message = _('Illustration was successfully updated')
    story_page_url = story_catalog.EDIT_STORY_PAGES_ILLUSTRATIONS
    variation_page_url = variation_catalog.EDIT_VARIATION_PAGES_ILLUSTRATIONS
    login_required = True

    def check_rights(self, obj, user):
        self.story = obj.story
        self.variation = obj.variation
        if self.variation:
            self.story = obj.variation.story
            self.catalog_page = story_catalog.CatalogPage(
                name=obj,
                parent=variation_catalog.EditVariationSubpage(
                    self.variation, url=self.variation_page_url))
        else:
            self.story = obj.story
            self.catalog_page = story_catalog.CatalogPage(
                name=obj,
                parent=story_catalog.EditStorySubpage(
                    self.story, url=self.story_page_url))
        return self.story.edit_right(user)

    def get_context_data(self, **kwargs):
        kwargs['story'] = self.story
        kwargs['variation'] = self.variation
        kwargs['catalog_page'] = self.catalog_page
        return super(EditIllustrationView, self).get_context_data(**kwargs)

    def get_success_url(self):
        return self.catalog_page.parent.url


class EditMaterialView(EditIllustrationView):
    template_name = 'stories/materials/material.haml'
    model = models.AdditionalMaterial
    form_class = materials_forms.AdditionalMaterialForm
    success_message = _('Additional material was successfully updated')
    story_page_url = story_catalog.EDIT_STORY_PAGES_MATERIALS
    variation_page_url = variation_catalog.EDIT_VARIATION_PAGES_MATERIALS


def get_story(story_id, user):
    try:
        story_id = int(story_id)
    except:
        raise http.Http404()
    story = shortcuts.get_object_or_404(models.Story, id=story_id)
    if not story.edit_right(user):
        raise http.Http404()
    return story


@decorators.login_required
def add_story_illustration(request, story_id):
    return materials_views.upload_illustration(
        request, get_story(story_id, request.user), None, None)


class AddMaterialView(BaseStoryAddView):
    template_name = 'stories/materials/material.haml'
    form_class = materials_forms.AdditionalMaterialForm
    parent_page_url = story_catalog.EDIT_STORY_PAGES_MATERIALS
    page_name = _('Add material')
    model = models.AdditionalMaterial
    success_message = _('Additional material was successfully added')

    def get_success_url(self):
        return urls.reverse('stories:' + self.parent_page_url, args=(
            self.parent_object.pk,))


class DeleteIllustrationView(
        djfw_views.RightsDetailMixin, generic.edit.BaseDeleteView):
    model = models.Illustration
    variation_url = variation_catalog.EDIT_VARIATION_PAGES_ILLUSTRATIONS
    story_url = story_catalog.EDIT_STORY_PAGES_ILLUSTRATIONS

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def check_rights(self, obj, user):
        self.story = obj.story
        self.variation = obj.variation
        return obj.edit_right(user)

    def get_success_url(self):
        if self.variation:
            return urls.reverse(
                'stories:' + self.variation_url, args=(self.variation.pk,))
        return urls.reverse('stories:' + self.story_url, args=(
            self.story.pk,))


class DeleteMaterialView(DeleteIllustrationView):
    model = models.AdditionalMaterial
    variation_url = variation_catalog.EDIT_VARIATION_PAGES_MATERIALS
    story_url = story_catalog.EDIT_STORY_PAGES_MATERIALS
