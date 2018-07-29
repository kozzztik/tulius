from django import urls
from django.apps import apps
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.views.generic.edit import UpdateView, BaseDeleteView

from djfw.uploader import handle_field_upload
from djfw.inlineformsets import get_formset
from djfw.sortable.views import SortableDetailViewMixin
from djfw.views import RightsDetailMixin
from djfw.subviews import SubCreateView
from tulius.games.views import MessageMixin
from .models import Story, Variation, Character, Avatar, Role, \
    AdditionalMaterial, Illustration, StoryAdmin, StoryAuthor
from .story_edit_forms import CharacterForm, EditStoryMainForm, \
    EditStoryTextsForm, StoryAuthorForm,\
    StoryAdminForm, VariationForm, AvatarForm
from .materials_forms import AdditionalMaterialForm, IllustrationForm
from .edit_story_cataloging import *
from .edit_variation_catalog import EDIT_VARIATION_PAGES_MATERIALS, \
    EDIT_VARIATION_PAGES_ILLUSTRATIONS, EditVariationSubpage
from .materials_views import upload_illustration
from djfw.custom_views import ActionableViewMixin, FormsetWidget


class StoryAdminMixin(RightsDetailMixin):
    model = Story
    page_url = None
    success_message = _('story was successfully updated')
    
    def check_rights(self, obj, user):
        return obj.edit_right(user)
    
    def get_context_data(self, **kwargs):
        if self.page_url:
            kwargs['catalog_page'] = EditStorySubpage(
                self.object, url=self.page_url)
        return super(StoryAdminMixin, self).get_context_data(**kwargs)
    
    def get_success_url(self):
        return urls.reverse('stories:' + self.page_url, args=(self.object.pk,))


class StoryMainView(StoryAdminMixin, MessageMixin, UpdateView):
    template_name = 'base_cataloged_navig_form_game.haml'
    form_class = EditStoryMainForm
    page_url = EDIT_STORY_PAGES_MAIN


class StoryTextsView(StoryAdminMixin, MessageMixin, UpdateView):
    template_name = 'stories/edit_story/texts.haml'
    form_class = EditStoryTextsForm
    page_url = EDIT_STORY_PAGES_TEXTS


class StoryFile():
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


class StoryGraphics(StoryAdminMixin, DetailView):
    template_name = 'stories/edit_story/graphics.haml'
    page_url = EDIT_STORY_PAGES_GRAPHICS
    
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
            raise Http404()
        return handle_field_upload(request, field, '%s.jpg' % (story.pk,))


class UsersFormsets:
    def __init__(
            self, data=None, instance=None, initial=None, static=True,
            **kwargs):
        self.authorformset = get_formset(
            Story, StoryAuthor, data, StoryAuthorForm, extra=1, static=static,
            instance=instance, params={'static': static})
        self.adminformset = get_formset(
            Story, StoryAdmin, data, StoryAdminForm, extra=1, static=static,
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


class StoryUsers(ActionableViewMixin, StoryAdminMixin, DetailView):
    template_name = 'stories/edit_story/users.haml'
    page_url = EDIT_STORY_PAGES_USERS
    
    def get_editable(self):
        return self.request.user.is_superuser
    
    widgets = {
        'authorformset': {
            'class': FormsetWidget, 'model': StoryAuthor,
            'table_class': 'table', 'editable': get_editable},
        'adminformset': {
            'class': FormsetWidget, 'model': StoryAdmin,
            'table_class': 'table', 'editable': get_editable}
    }


class EditStoryVariations(
        StoryAdminMixin, SortableDetailViewMixin, DetailView):
    template_name = 'stories/edit_story/variations.haml'
    sortable_key = "var_"
    sortable_field = 'order'
    sortable_model = Variation
    page_url = EDIT_STORY_PAGES_VARIATIONS


class BaseStoryAddView(StoryAdminMixin, MessageMixin, SubCreateView):
    parent_model = Story
        
    def check_parent_rights(self, obj, user):
        return self.check_rights(obj, user)
    
    def get_context_data(self, **kwargs):
        kwargs['form_submit_title'] = _("add")
        kwargs['catalog_page'] = CatalogPage(
            name=self.page_name,
            parent=EditStorySubpage(
                self.parent_object, url=self.parent_page_url))
        return super(BaseStoryAddView, self).get_context_data(**kwargs)


class AddVariationView(BaseStoryAddView):
    template_name = 'stories/edit_story/add_variation.haml'
    form_class = VariationForm
    parent_page_url = EDIT_STORY_PAGES_VARIATIONS
    page_name = _('Add new variation')
    model = Variation
    
    def form_valid(self, form):
        with transaction.commit_on_success():
            variation = form.save(commit=False)
            variation.story = self.parent_object
            variation.save()
            gameforum = apps.get_app_config('gameforum').site
            variation.thread = gameforum.core.create_gameforum(
                self.request.user, variation)
            variation.save()
            characters = Character.objects.filter(story=self.parent_object)
            for character in characters:
                role = Role(variation=variation, character=character)
                role.avatar = character.avatar
                role.name = character.name
                role.description = character.description
                role.show_in_character_list = character.show_in_character_list
                role.save()
            messages.success(
                self.request, _('variation was successfully added'))
            return HttpResponseRedirect(variation.get_absolute_url())


class EditStoryCharacters(
        StoryAdminMixin, SortableDetailViewMixin, DetailView):
    template_name = 'stories/edit_story/characters.haml'
    sortable_key = "char_"
    sortable_field = 'order'
    sortable_model = Character
    page_url = EDIT_STORY_PAGES_CHARACTERS


class CharacterFormMixin:
    parent_page_url = EDIT_STORY_PAGES_CHARACTERS

    def get_form_kwargs(self):
        kwargs = super(CharacterFormMixin, self).get_form_kwargs()
        kwargs['story'] = self.parent_object
        return kwargs

    def get_success_url(self):
        return urls.reverse(
            'stories:' + self.parent_page_url, args=(self.parent_object.pk,))


class AddCharacterView(CharacterFormMixin, BaseStoryAddView):
    template_name = 'base_cataloged_navig_form_game.haml'
    form_class = CharacterForm
    model = Character
    page_name = _('Add new character')
    success_message = _('character was successfully added')


class CharacterView(
        CharacterFormMixin, RightsDetailMixin, MessageMixin, UpdateView):
    template_name = 'base_cataloged_navig_form_game.haml'
    model = Character
    form_class = CharacterForm
    success_message = _('character was successfully updated')
    
    def check_rights(self, obj, user):
        self.parent_object = obj.story
        return self.parent_object.edit_right(user)

    def get_context_data(self, **kwargs):
        kwargs['story'] = self.parent_object
        kwargs['catalog_page'] = CatalogPage(
            name=self.object,
            parent=EditStorySubpage(
                self.parent_object, url=self.parent_page_url))
        return super(CharacterView, self).get_context_data(**kwargs)


class StoryAvatarsView(StoryAdminMixin, DetailView):
    template_name = 'stories/edit_story/avatars.haml'
    page_url = EDIT_STORY_PAGES_AVATARS


class StoryIllustrationsView(StoryAdminMixin, DetailView):
    template_name = 'stories/materials/illustrations.haml'
    page_url = EDIT_STORY_PAGES_ILLUSTRATIONS
    
    def get_context_data(self, **kwargs):
        kwargs['illustrations'] = Illustration.objects.filter(story=self.object)
        return super(StoryIllustrationsView, self).get_context_data(**kwargs)


class StoryMaterialsView(StoryAdminMixin, DetailView):
    template_name = 'stories/materials/materials.haml'
    page_url = EDIT_STORY_PAGES_MATERIALS
    
    def get_context_data(self, **kwargs):
        kwargs['materials'] = AdditionalMaterial.objects.filter(
            story=self.object)
        return super(StoryMaterialsView, self).get_context_data(**kwargs)


class StoryDeleteAvatarView(RightsDetailMixin, BaseDeleteView):
    model = Avatar
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def check_rights(self, obj, user):
        self.story = obj.story
        return obj.story.edit_right(user)
    
    def get_success_url(self):
        return urls.reverse(
            'stories:' + EDIT_STORY_PAGES_AVATARS, args=(self.story.pk,))


class EditAvatarView(RightsDetailMixin, MessageMixin, UpdateView):
    template_name = 'stories/edit_story/avatar.haml'
    model = Avatar
    form_class = AvatarForm
    success_message = _('avatar was successfully updated')
    parent_page_url = EDIT_STORY_PAGES_AVATARS
    
    def check_rights(self, obj, user):
        self.story = obj.story
        return obj.story.edit_right(user)

    def get_context_data(self, **kwargs):
        kwargs['story'] = self.story
        kwargs['catalog_page'] = CatalogPage(
            name=self.object,
            parent=EditStorySubpage(self.story, url=self.parent_page_url))
        return super(EditAvatarView, self).get_context_data(**kwargs)

    def get_success_url(self):
        return urls.reverse('stories:' + self.parent_page_url, args=(
            self.story.pk,))


class EditIllustrationView(RightsDetailMixin, MessageMixin, UpdateView):
    template_name = 'stories/materials/illustration.haml'
    model = Illustration
    form_class = IllustrationForm
    success_message = _('Illustration was successfully updated')
    story_page_url = EDIT_STORY_PAGES_ILLUSTRATIONS
    variation_page_url = EDIT_VARIATION_PAGES_ILLUSTRATIONS
    login_required = True
    
    def check_rights(self, obj, user):
        self.story = obj.story
        self.variation = obj.variation
        if self.variation:
            self.story = obj.variation.story
            self.catalog_page = CatalogPage(
                name=obj,
                parent=EditVariationSubpage(
                    self.variation, url=self.variation_page_url))
        else:
            self.story = obj.story
            self.catalog_page = CatalogPage(
                name=obj,
                parent=EditStorySubpage(self.story, url=self.story_page_url))
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
    model = AdditionalMaterial
    form_class = AdditionalMaterialForm
    success_message = _('Additional material was successfully updated')
    story_page_url = EDIT_STORY_PAGES_MATERIALS
    variation_page_url = EDIT_VARIATION_PAGES_MATERIALS


def get_story(story_id, user):
    try:
        story_id = int(story_id)
    except:
        raise Http404()
    story = get_object_or_404(Story, id=story_id)
    if not story.edit_right(user):
        raise Http404()
    return story


@login_required
def add_story_illustration(request, story_id):
    return upload_illustration(
        request, get_story(story_id, request.user), None, None)


class AddMaterialView(BaseStoryAddView):
    template_name = 'stories/materials/material.haml'
    form_class = AdditionalMaterialForm
    parent_page_url = EDIT_STORY_PAGES_MATERIALS
    page_name = _('Add material')
    model = AdditionalMaterial
    success_message = _('Additional material was successfully added')

    def get_success_url(self):
        return urls.reverse('stories:' + self.parent_page_url, args=(
            self.parent_object.pk,))


class DeleteIllustrationView(RightsDetailMixin, BaseDeleteView):
    model = Illustration
    variation_url = EDIT_VARIATION_PAGES_ILLUSTRATIONS
    story_url = EDIT_STORY_PAGES_ILLUSTRATIONS

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
        else:
            return urls.reverse('stories:' + self.story_url, args=(
                self.story.pk,))


class DeleteMaterialView(DeleteIllustrationView):
    model = AdditionalMaterial
    variation_url = EDIT_VARIATION_PAGES_MATERIALS
    story_url = EDIT_STORY_PAGES_MATERIALS
