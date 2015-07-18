from django import template

register = template.Library()

@register.inclusion_tag('cataloging/catalog_breadcrumbs.html', takes_context=True)
def catalog_breadcrumbs(context):
    return {
        'list': context['catalog_page'].get_breadcrumbs(),
    }
    
class CatalogIndex(template.Node):

    def __init__(self, catalog_page):
        self.catalog_page_name = catalog_page

    def render(self, context):
        catalog_page = context[self.catalog_page_name]
        return catalog_page.catalog_index()
    
class CatalogCaption(CatalogIndex):
    
    def render(self, context):
        catalog_page = context[self.catalog_page_name]
        return catalog_page.catalog_caption()
        
@register.tag(name="catalog_index")
def do_catalog_index(parser, token):
    try:
        tag_name, catalog_page = token.split_contents()
    except ValueError:
        msg = '%r tag requires a single argument' % tag_name
        raise template.TemplateSyntaxError(msg)
    return CatalogIndex(catalog_page)
    
@register.tag(name="catalog_caption")
def do_catalog_caption(parser, token):
    try:
        tag_name, catalog_page = token.split_contents()
    except ValueError:
        msg = '%r tag requires a single argument' % tag_name
        raise template.TemplateSyntaxError(msg)
    return CatalogCaption(catalog_page)