import asyncio

from asgiref.sync import sync_to_async
from django import http
from django.conf import settings

from djfw.flatpages import views


def flatpage_middleware(get_response):
    if asyncio.iscoroutinefunction(get_response):
        return AsyncFlatpageFallbackMiddleware(get_response)
    return FlatpageFallbackMiddleware(get_response)


class FlatpageFallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code != 404:
            # No need to check for a flatpage for non-404 responses.
            return response
        try:
            return views.flatpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except http.Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response


class AsyncFlatpageFallbackMiddleware:
    _is_coroutine = asyncio.coroutines._is_coroutine

    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        response = await self.get_response(request)

        if response.status_code != 404:
            # No need to check for a flatpage for non-404 responses.
            return response
        try:
            return await sync_to_async(
                views.flatpage, thread_sensitive=False)(
                request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except http.Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response


flatpage_middleware.async_capable = True
