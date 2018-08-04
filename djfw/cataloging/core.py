
class CatalogPage():
    """
        Class for page in Catalog tree
    """
    
    name = ''
    url = ''
    is_index = False
    parent = None
    subpages_cache = []
    
    def get_subpages_internal(self):
        return []
    
    def get_subpages(self):
        if not self.subpages_cache:
            subpages_cache = self.get_subpages_internal()
        return subpages_cache
    
    def get_subpage(self, url):
        subpages = self.get_subpages()
        for page in subpages:
            if page.url == url:
                return page
        return None
        
    def __init__(
            self, name='', url='', instance=None, is_index=False, parent=None):
        self.is_index = is_index
        self.parent = parent
        if instance:
            self.name = str(instance)
            self.url = instance.get_absolute_url()
        else:
            self.name = str(name)
            self.url = url
    
    def get_index(self):
        if self.is_index:
            return self
        if self.parent:
            return self.parent.get_index()
        return None
    
    def get_breadcrumbs(self):
        if self.parent:
            return self.parent.get_breadcrumbs() + [self]
        return [self]
            
    def render_selected(self):
        return self.name
    
    def render(self):
        return '<a href="%s">%s</a>' % (self.url, self.name)
        
    def get_caption(self):
        caption = self.name
        if caption:
            caption = caption[0].upper() + caption[1:]
        return caption
        
    def catalog_index(self, subpage='', rendered_subpage=''):
        subpages = self.get_subpages()
        if subpages:
            result = ''
            for page in subpages:
                if page.name == subpage:
                    if rendered_subpage:
                        result = '%s<li>%s</li>' % (result, rendered_subpage,)
                    else:
                        result = '%s<li>%s</li>' % (
                            result, page.render_selected(),)
                else:
                    result = '%s<li>%s</li>' % (result, page.render(),)
            result = '<ul class="catalogindex">%s</ul>' % (result, )
        else:
            if rendered_subpage:
                result = '%s<ul><li>%s</li></ul>' % (
                    self.render(), rendered_subpage)
            else:
                result = self.name
            result = '<ul class="catalogindex"><li>%s</li></ul>' % (result,)
        if self.is_index or (not self.parent):
            return result
        return self.parent.catalog_index(self.name, result)
            
    def catalog_caption(self):
        if self.is_index or (not self.parent):
            return self.get_caption()
        return "%s - %s" % (
            self.parent.catalog_caption(), self.get_caption())
