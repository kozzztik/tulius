from tulius.forum import plugins
from tulius.stories import models as stories_models


class VariationMixin(plugins.BaseAPIView):
    variation = None

    def dispatch(self, request, *args, **kwargs):
        self.variation = stories_models.Variation.objects.get(
            pk=int(kwargs['variation_id']))
        return super(VariationMixin, self).dispatch(request, *args, **kwargs)
