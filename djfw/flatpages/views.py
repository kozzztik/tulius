from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from .models import FlatPage


DEFAULT_TEMPLATE = 'flatpages/default.haml'

# This view is called from FlatpageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching flatpage exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.


def flatpage(request, url):
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
    f = get_object_or_404(FlatPage, url__exact=url, is_enabled=True)
    return render_flatpage(request, f)


@csrf_protect
def render_flatpage(request, f):
    """
    Internal interface to the flat page view.
    """
    template_name = getattr(settings, 'FLATPAGES_TEMPLATE', DEFAULT_TEMPLATE)
    template = TemplateResponse(request, template_name, {'flatpage': f})
    template.render()
    return template


class FlatpagesList(TemplateView):
    template_name = 'flatpages/list.haml'

    def get_context_data(self, **kwargs):
        return {'flatpages': FlatPage.objects.all()}
