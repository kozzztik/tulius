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
        import logging
        logger = logging.getLogger('forum_debug')
        logger.error(
            f'{request.path} - {request.user.is_authenticated}'
            f' - {self.user} - {request.session.session_key}')
        if self.require_user and (not request.user.is_authenticated):
            return http.HttpResponseForbidden()
        response = super().dispatch(request, *args, **kwargs)
        if isinstance(response, http.HttpResponse):
            return response
        return http.JsonResponse(response)

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return transaction.non_atomic_requests(view)
