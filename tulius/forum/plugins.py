from django import http
from django.db import transaction
from django.views.generic import base


class BaseAPIView(base.ContextMixin, base.View):
    """
    Transform view context to json response.
    """
    require_user = False
    user = None

    def get_context_data(self, **kwargs):
        return {}

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = self.request.user
        if self.require_user and (not request.user.is_authenticated):
            return http.HttpResponseForbidden()
        response = super(BaseAPIView, self).dispatch(
            request, *args, **kwargs)
        if isinstance(response, http.HttpResponse):
            return response
        return http.JsonResponse(response)

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(BaseAPIView, cls).as_view(**initkwargs)
        return transaction.non_atomic_requests(view)
