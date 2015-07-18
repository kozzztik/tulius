#from django.core.exceptions import ImproperlyConfigured
from django.conf.urls import patterns
from django.conf import settings

class SitesManager():
    sites = []
    
    def add_site(self, site):
        obj = self.get_site(site.site_id)
        if not obj:
            self.sites += [site]
    
    def get_site(self, site_id):
        for site in self.sites:
            if site.site_id == site_id:
                return site
        return None 
    
sites_manager = SitesManager()

class SiteCore(object):
    def __init__(self, site):
        self.content = {}
        self.site = site
        self.name = site.name
        
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return self.content[attr]
    
    def __getitem__(self, key):
        return self.content[key]

    def __setitem__(self, key, value):
        self.content[key] = value
        
class BaseForumSite(object):
    plugins = {}
    plugin_classes = ()
    core = None
    templates = None
    urlizer = None
    signals = None
    
    def __init__(self, name='forum', app_name='forum', site_id=None, plugins=()):
        self.app_name = app_name
        self.name = name
        self.site_id = site_id
        self.plugin_classes = plugins
        self.core = SiteCore(self)
        self.templates = SiteCore(self)
        self.urlizer = SiteCore(self)
        self.signals = SiteCore(self)
        self.init_core()
        self.models = self.core.models
        self.init_plugins()
        sites_manager.add_site(self)
    
    def init_core(self):
        import models
        self.core.models = models

    def get_own_urls(self):
        return patterns('')
    
    def check_dependencies(self):
        for plugin in self.plugins.values():
            plugin.check_dependencies(self.plugins)
            
    def init_plugins(self):
        self.plugins = {}
        for plugin_class in self.plugin_classes:
            plugin = plugin_class(self)
            self.plugins[plugin_class.__name__] = plugin
            self.core.content.update(plugin.core)
            self.templates.content.update(plugin.templates)
            self.urlizer.content.update(plugin.urlizer)
            self.signals.content.update(plugin.signals)
        for plugin in self.plugins.itervalues():
            plugin.post_init()
        if settings.DEBUG:
            self.check_dependencies()

    def get_urls(self):
        urlpatterns = self.get_own_urls()
        for plugin in self.plugins.values():
            urlpatterns += plugin.get_urls()

        return urlpatterns
    
    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name
    
class ForumSite(BaseForumSite):

    def init_core(self):
        super(ForumSite, self).init_core()
        self.templates['base'] = 'forum/base.haml'
        self.templates['form_field'] = 'snippets/form_field.haml'
        self.templates['init_editor'] = 'wysibb/init.html'
        self.templates['actions'] = 'forum/snippets/forum_actions_menu.haml'