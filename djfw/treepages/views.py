from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.query_utils import Q
from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.utils import translation
from .models import TreePage

# This view is called from FlatpageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching flatpage exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.
def treepage(request, url):
    """
    Public interface to the flat page view.

    Models: `flatpages.flatpages`
    Templates: Uses the template defined by the ``template_name`` field,
        or `flatpages/default.html` if template_name is not defined.
    Context:
        flatpage
            `flatpages.flatpages` object
    """
    if not url.endswith('/') and settings.APPEND_SLASH:
        return HttpResponseRedirect("%s/" % request.path)
    if not url.startswith('/'):
        url = "/" + url
    lang = translation.get_language()
    query = Q(language=lang) | Q(language__isnull=True)
    f = get_object_or_404(TreePage.objects.filter(query), url__exact=url, is_enabled=True)
    return render_treepage(request, f)

@csrf_protect
def render_treepage(request, f):
    """
    Internal interface to the flat page view.
    """
    template_name = getattr(settings, 'TREEPAGES_TEMPLATE', 'treepages/default.haml')
    t = loader.get_template(template_name)

    c = RequestContext(request, {
        'treepage': f,
    })
    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, TreePage, f.id)
    return response

def list(request, template_name='treepages/list.haml'):
    lang = translation.get_language()
    query = Q(language=lang) | Q(language__isnull=True)
    treepages = TreePage.objects.filter(parent=None).filter(query)
    c = RequestContext(request, locals())
    t = loader.get_template(template_name)
    return  HttpResponse(t.render(c))

def rebuild_treepages(request):
    TreePage.objects.rebuild()
    return HttpResponseRedirect('/')