from django.conf.urls import url

# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin, BasePluginView
from .views import DoTrustmark


class TrustmarksPlugin(ForumPlugin):
    max_val = 3

    def trustmarks_url(self):
        return self.reverse('do_trustmark')

    def mark_to_percents(self, mark_value):
        return int(50 + (mark_value * 50 / self.max_val))

    def recalc_role_trust(self, role):
        trustmarks = self.site.gamemodels.Trustmark.objects.filter(role=role)
        markcount = len(trustmarks)
        marksum = 0
        for mark in trustmarks:
            marksum += mark.value
        if markcount:
            marksum = (marksum / markcount)
        value = self.mark_to_percents(marksum)
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        role.trust_value = value
        role.save()
        return value

    def init_core(self):
        self.urlizer['trustmarks'] = self.trustmarks_url
        self.core['mark_to_percents'] = self.mark_to_percents
        self.core['recalc_role_trust'] = self.recalc_role_trust

    def get_urls(self):
        return [
            url(
                r'^do_trustmark/$',
                DoTrustmark.as_view(self),
                name='do_trustmark'),
        ]
