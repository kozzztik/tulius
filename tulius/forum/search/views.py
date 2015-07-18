from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import get_current_timezone
#TODO: needs to be fixed
from tulius.forum.plugins import BasePluginView
from django.core.exceptions import PermissionDenied
from .forms import ExtendedSearchForm
from django.views.generic import View
import json
import datetime
from django.http import HttpResponse
from tulius.models import User

def get_datetime(text):
    date = None
    try:
        date = datetime.datetime.strptime(text, "%d.%m.%Y")
    except:
        pass
    return datetime.datetime(date.year, date.month, date.day, tzinfo=get_current_timezone())
    
class ExtendedSearchView(BasePluginView):
    template_name = 'search_form'
    
    def get_context_data(self, **kwargs):
        context = super(ExtendedSearchView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        thread = self.site.models.Thread.objects.get(parent=None, tree_id=pk)
        thread = self.site.core.get_parent_thread(self.request.user, thread.pk)
        self.object = thread
        if not thread.read_right(self.request.user):
            raise PermissionDenied()
        threads = self.core.threads_search_list(self.request.user, thread)
        threads = [thread] + threads
        threads = [(thread.id, '- ' * (thread.level) + thread.title) for thread in threads]
        self.form = ExtendedSearchForm(threads, data=self.request.POST or None)
        context['form'] = self.form
        context['parent_thread'] = self.object
        context['form_submit_title'] = _(u'Search')
        context['form_action'] = thread.search_url
        return context
    
class SearchView(ExtendedSearchView):
    template_name = 'search'
    
    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        form = self.form
        if not form.is_valid():
            context['form_invalid'] = True
            return context
        data = form.cleaned_data
        conditions = []
        parent_thread = self.object
        parent_thread.write_right = False
        comments = self.site.models.Comment.objects.select_related('parent').filter(plugin_id=self.plugin.site_id)
        comments = comments.filter(parent__tree_id=parent_thread.tree_id)
        filter_thread = data.get('thread', None)
        filter_users = data.get('users', [])
        filter_not_users = data.get('not_users', [])
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
        
        if filter_users:
            conditions += [_(u'From users: ') + ', '.join([user.username for user in filter_users])]
            comments = comments.filter(user__in=filter_users)
            
        if filter_not_users:
            conditions += [_(u'Not from users: ') + ', '.join([user.username for user in filter_not_users])]
            comments = comments.exclude(user__in=filter_not_users)

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
        return context

    def post(self, request, pk, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class SearchVariantsView(View):
    def get(self, request, *args, **kwargs):
        q = self.request.GET['q']
        res = []
        if len(q) > 2:
            res = User.objects.filter(username__istartswith=q)[:5]
        res = [{'id': str(user.id), 'text': user.username} for user in res]
        s = json.dumps(res)
        return HttpResponse(s)