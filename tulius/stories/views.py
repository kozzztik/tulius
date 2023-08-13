from django import http
from django import shortcuts
from django.contrib import messages
from django.views import generic
from django.contrib.auth import decorators
from django.utils.translation import gettext_lazy as _

from djfw import views as djfw_views
from djfw.cataloging import core as cataloging

from tulius.stories import catalog
from tulius.stories import forms
from tulius.stories import materials_views
from tulius.stories import models


def filter_by_author(stories, author):
    storyauthor = models.StoryAuthor.objects.filter(
        user__id=author).values('story').distinct()
    storylist = [author['story'] for author in storyauthor]
    return stories.filter(pk__in=storylist)


class IndexView(generic.TemplateView):
    template_name = 'stories/index.haml'

    def get_context_data(self, **kwargs):
        stories_filter_form = forms.StoryFilterForm(self.request.GET or None)
        stories = models.Story.objects.order_by('-creation_year')
        total_stories_count = stories.count()
        if self.request.GET:
            if ('filter_by_genre' in self.request.GET) and self.request.GET[
                    'filter_by_genre']:
                stories = stories.filter(
                    genres=self.request.GET['filter_by_genre'])
            if ('filter_by_author' in self.request.GET) and self.request.GET[
                    'filter_by_author']:
                stories = filter_by_author(stories, self.request.GET[
                    'filter_by_author'])
            if ('filter_by_creation_year' in self.request.GET) and \
                    self.request.GET['filter_by_creation_year']:
                stories = stories.filter(creation_year=self.request.GET[
                    'filter_by_creation_year'])
        stories = [
            story for story in stories
            if ((not story.hidden) or story.edit_right(self.request.user))]
        filtered_stories_count = len(stories)
        filtered = self.request.GET and (
            filtered_stories_count != total_stories_count)
        for story in stories:
            story.editable = story.edit_right(self.request.user)
            story.authors.all()
        return {
            'stories_filter_form': stories_filter_form,
            'filtered_stories_count': filtered_stories_count,
            'filtered': filtered,
            'total_stories_count': total_stories_count,
            'stories': stories,
            'add_form': forms.AddStoryForm(),
            'catalog_page': catalog.stories_catalog_page(),
        }


class AddStory(djfw_views.LoginRequiredMixin, djfw_views.AjaxModelFormView):
    form_class = forms.AddStoryForm

    def get_success_url(self):
        return self.model.get_edit_url()

    def model_setup(self, model):
        model.hidden = True
        messages.success(self.request, _('story was successfully added'))


def get_story_page(story):
    return cataloging.CatalogPage(
        instance=story, parent=catalog.stories_catalog_page(), is_index=True)


class StoryView(generic.DetailView):
    template_name = 'stories/story.haml'
    model = models.Story

    def get_context_data(self, **kwargs):
        story = self.object
        if story.edit_right(self.request.user):
            story.edit_url = story.get_edit_url()
        characters = models.Character.objects.filter(
            story=story, show_in_character_list=True)
        authors = models.StoryAuthor.objects.filter(story=story)
        materials = models.AdditionalMaterial.objects.filter(
            story=story, admins_only=False)
        return {
            'story': story, 'characters': characters,
            'materials': materials, 'authors': authors}


class CharacterInfoView(generic.DetailView):
    template_name = 'stories/role_info.haml'
    model = models.Character

    def get_context_data(self, **kwargs):
        character = self.object
        story = character.story
        if (not story) or (not character.show_in_character_list):
            raise http.Http404()
        return locals()


@decorators.login_required
def edit_illustration_reload(request, illustration_id):
    try:
        illustration_id = int(illustration_id)
    except ValueError as exc:
        raise http.Http404() from exc
    illustration = shortcuts.get_object_or_404(
        models.Illustration, id=illustration_id)
    if not illustration.edit_right(request.user):
        raise http.Http404()
    return materials_views.upload_illustration(
        request, illustration.story, illustration.variation, illustration)


class MaterialView(djfw_views.RightsDetailMixin, generic.DetailView):
    template_name = 'stories/material.haml'
    model = models.AdditionalMaterial

    def check_rights(self, obj, user):
        if obj.admins_only and (not obj.edit_right(user)):
            return False
        return obj.read_right(user)

    def get_context_data(self, **kwargs):
        kwargs['catalog_page'] = cataloging.CatalogPage(
            instance=self.object, parent=get_story_page(self.object.story))
        return super().get_context_data(**kwargs)
