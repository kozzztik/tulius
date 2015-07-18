from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import get_current_timezone
#TODO: needs to be fixed
from tulius.forum.plugins import BasePluginView
from tulius.stories.models import Variation, Role
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from .forms import ExtendedSearchForm

import datetime

def get_datetime(text):
    date = None
    try:
        date = datetime.datetime.strptime(text, "%d.%m.%Y")
    except:
        pass
    return datetime.datetime(date.year, date.month, date.day, tzinfo=get_current_timezone())
    
class ExtendedSearchView(BasePluginView, DetailView):
    template_name = 'search_form'
    model = Variation
    
    def get_context_data(self, **kwargs):
        context = super(ExtendedSearchView, self).get_context_data(**kwargs)
        variation = self.get_object()
        self.object = variation
        if (not variation.game) and (not variation.edit_right(self.request.user)):
            raise PermissionDenied()
        if variation.game and (not variation.game.read_right(self.request.user)):
            raise PermissionDenied()
        roles = Role.objects.filter(variation=variation, show_in_character_list=True)
        threads = self.core.threads_search_list(self.request.user, variation.thread)
        threads = [variation.thread] + threads
        threads = [(thread.id, '- ' * (thread.level) + thread.title) for thread in threads]
        self.form = ExtendedSearchForm(roles, threads, data=self.request.POST or None)
        context['form'] = self.form
        context['variation'] = self.object
        context['form_submit_title'] = _(u'Search')
        context['form_action'] = variation.thread.search_url
        return context
    
class SearchView(ExtendedSearchView):
    template_name = 'search'
    
    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        variation = self.object
        form = self.form
        if not form.is_valid():
            context['form_invalid'] = True
            return context
        data = form.cleaned_data
        conditions = []
        parent_thread = self.site.core.get_parent_thread(self.request.user, variation.thread_id)
        parent_thread.write_right = False
        comments = self.site.models.Comment.objects.select_related('parent').filter(plugin_id=self.plugin.site_id)
        comments = comments.filter(parent__tree_id=variation.thread.tree_id)
        filter_thread = data.get('thread', None)
        filter_roles = data.get('roles', [])
        filter_not_roles = data.get('not_roles', [])
        filter_date_from = data.get('date_from', [])
        filter_date_to = data.get('date_to', [])
        filter_text = data.get('text', [])
        
        if filter_thread:
            thread = self.site.models.Thread.objects.get(pk=filter_thread)
            if thread.read_right(self.request.user):
                if thread.room:
                    conditions += [_(u'In room: ') + thread.title]
                else:
                    conditions += [_(u'In thread: ') + thread.title]
                comments = comments.filter(parent__lft__gte=thread.lft, parent__rght__lte=thread.rght)
        
        filter_roles = [role for role in filter_roles if (role.variation_id == variation.id)]
        filter_roles = [role for role in filter_roles if role.show_in_character_list]
        filter_not_roles = [role for role in filter_not_roles if (role.variation_id == variation.id)]
        filter_not_roles = [role for role in filter_not_roles if role.show_in_character_list]
        if filter_roles:
            conditions += [_(u'From characters: ') + ', '.join([role.name for role in filter_roles])]
            comments = comments.filter(data1__in=[role.id for role in filter_roles])
            
        if filter_not_roles:
            conditions += [_(u'Not from characters: ') + ', '.join([role.name for role in filter_not_roles])]
            comments = comments.exclude(data1__in=[role.id for role in filter_not_roles])

        if filter_date_from:
            date = get_datetime(filter_date_from)
            if date:
                comments = comments.filter(create_time__gte=date)
                conditions += [_(u'From date: ') + filter_date_from]

        if filter_date_to:
            date = get_datetime(filter_date_to)
            if date:
                comments = comments.filter(create_time__lte=date)
                conditions += [_(u'To date: ') + filter_date_to]

        if filter_text:
            conditions += [_(u'With text: ') + filter_text]
            comments = comments.filter(body__icontains=filter_text)
        comments = comments[:50]
        search_results = [comment for comment in comments if comment.parent.read_right(self.request.user)]
        self.site.signals.read_comments.send(parent_thread, comments=search_results, user=self.request.user)
        context['conditions'] = conditions
        context['posts_on_page'] = self.core.models.COMMENTS_ON_PAGE
        context['search_results'] = search_results
        context['parent_thread'] = parent_thread
        return context

    def post(self, request, pk, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
