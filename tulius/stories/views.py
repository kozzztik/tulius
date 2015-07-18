from django.views.generic import DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
from django.contrib import messages
from djfw.cataloging.core import CatalogPage
from .models import *
from .forms import *
from .materials_views import upload_illustration
from .catalog import stories_catalog_page

def filter_by_author(stories, author):
    storyauthor=StoryAuthor.objects.filter(user__id=author).values('story').distinct()
    storylist = [author['story'] for author in storyauthor]
    return stories.filter(pk__in=storylist)
    
class TestView(TemplateView):
    template_name='stories/index.haml'
    def get_context_data(self, **kwargs):
        from djfw.autocomplete.widget import AutocompleteWidget
        from tulius.models import User
        w = AutocompleteWidget(User, 'grtgrtg')
        t = User.objects.filter(id=31)
        w.render('test_name', value=t, attrs={'id': 'dfdf'})
        
class IndexView(TemplateView):
    template_name='stories/index.haml'
    def get_context_data(self, **kwargs):
        stories_filter_form = StoryFilterForm(self.request.GET or None)
        stories = Story.objects.order_by('-creation_year')
        catalog_page = stories_catalog_page()
        total_stories_count = stories.count()
        if self.request.GET:
            if ('filter_by_genre' in self.request.GET) and self.request.GET['filter_by_genre']:
                stories = stories.filter(genres=self.request.GET['filter_by_genre'])
            if ('filter_by_author' in self.request.GET) and self.request.GET['filter_by_author']:
                stories = filter_by_author(stories, self.request.GET['filter_by_author'])
            if ('filter_by_creation_year' in self.request.GET) and self.request.GET['filter_by_creation_year']:
                stories = stories.filter(creation_year=self.request.GET['filter_by_creation_year'])
        stories = [story for story in stories if ((not story.hidden) or story.edit_right(self.request.user))]
        filtered_stories_count = len(stories)
        filtered = self.request.GET and (filtered_stories_count <> total_stories_count)
        add_form = AddStoryForm()
        for story in stories:
            story.editable = story.edit_right(self.request.user)
            story.authors.all()
        return locals()

from djfw.views import AjaxModelFormView, LoginRequiredMixin, RightsDetailMixin

class AddStory(LoginRequiredMixin, AjaxModelFormView):
    form_class = AddStoryForm

    def get_success_url(self):
        return self.model.get_edit_url()
    
    def model_setup(self, model):
        model.hidden = True
        messages.success(self.request, _('story was successfully added'))
    
def get_story_page(story):
    return CatalogPage(instance=story, parent=stories_catalog_page(), is_index=True)
    
class StoryView(DetailView):
    template_name='stories/story.haml'
    model = Story
    def get_context_data(self, **kwargs):
        story = self.object
        if story.edit_right(self.request.user):
            story.edit_url = story.get_edit_url()
        characters = Character.objects.filter(story=story, show_in_character_list=True)
        authors = StoryAuthor.objects.filter(story=story)
        materials = AdditionalMaterial.objects.filter(story=story, admins_only=False)
        return {'story': story, 'characters': characters, 'materials': materials, 'authors': authors}
    
class CharacterInfoView(DetailView):
    template_name='stories/role_info.haml'
    model = Character
    def get_context_data(self, **kwargs):
        character = self.object
        story = character.story
        if (not story) or (not character.show_in_character_list):
            raise Http404()
        return locals()
    
@login_required
def edit_illustration_reload(request, illustration_id):
    try:
        illustration_id = int(illustration_id)
    except:
        raise Http404()
    illustration = get_object_or_404(Illustration, id=illustration_id)
    if not illustration.edit_right(request.user):
        raise Http404()
    return upload_illustration(request, illustration.story, illustration.variation, illustration)
            
class MaterialView(RightsDetailMixin, DetailView):
    template_name='stories/material.haml'
    model = AdditionalMaterial
    
    def check_rights(self, obj, user):
        if obj.admins_only and (not obj.edit_right(user)):
            return False
        return obj.read_right(user)
    
    def get_context_data(self, **kwargs):
        kwargs['catalog_page'] = CatalogPage(instance=self.object, parent=get_story_page(self.object.story))
        return super(MaterialView, self).get_context_data(**kwargs)