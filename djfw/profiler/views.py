from django.utils.translation import ugettext_lazy as _
from .time_selector import TimePeriodView
from .graphs import sunlignt_graph, time_period_graph, time_period_graph_sum, distribution_graph
    
class AuditoryReport(TimePeriodView):
    template_name='profiler/auditory.html'
    def get_context_data(self, **kwargs):
        return {'data': time_period_graph_sum(self.request)}

class LoadingReport(TimePeriodView):
    template_name='profiler/loading.html'
    def get_context_data(self, **kwargs):
        return {'graph': time_period_graph(self.request, 'module')}

class BrowsersReport(TimePeriodView):
    template_name='profiler/sunlignt.html'
    def get_context_data(self, **kwargs):
        graph = sunlignt_graph(self.request, 'browser', 'browser_version')
        graph['name'] = _("Browsers")
        return {'graph': graph}

class OsesReport(TimePeriodView):
    template_name='profiler/sunlignt.html'
    def get_context_data(self, **kwargs):
        graph = sunlignt_graph(self.request, 'os', 'os_version')
        graph['name'] = _("Operating systems")
        return {'graph': graph}

class ModulesReport(TimePeriodView):
    template_name='profiler/sunlignt.html'
    def get_context_data(self, **kwargs):
        graph = sunlignt_graph(self.request, 'module_name', 'func_name')
        graph['name'] = _("Modules")
        graph['category_name'] = _("Module")
        graph['id'] = 'modules_call'
        for category in graph['data']:
            for elem in category['data']:
                elem['label'] = elem['name']
        return {'graph': graph}
    
class MobilesReport(TimePeriodView):
    template_name='profiler/sunlignt.html'
    def get_context_data(self, **kwargs):
        graph = sunlignt_graph(self.request, 'mobile')
        graph['name'] = _("Mobile devices")
        graph['category_name'] = _("Type")
        for category in graph['data']:
            if category['label']:
                category['label'] = _("Mobile")
            else:
                category['label'] = _("Not mobile")
        return {'graph': graph}

class DevicesReport(TimePeriodView):
    template_name='profiler/sunlignt.html'
    def get_context_data(self, **kwargs):
        graph = sunlignt_graph(self.request, 'device')
        graph['name'] = _("Devices")
        for category in graph['data']:
            if not category['label']:
                category['label'] = "-"
        return {'graph': graph}

class DistributionReport(TimePeriodView):
    template_name='profiler/distribute.html'
    def get_context_data(self, **kwargs):
        return {'data': distribution_graph(self.request)}
    