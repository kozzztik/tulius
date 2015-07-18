from django import template
from django.conf import settings
from tulius.flatpages.models import FlatPage

register = template.Library()

class FlatpageNode(template.Node):
    def __init__(self, context_name, starts_with=None):
        self.context_name = context_name
        if starts_with:
            self.starts_with = template.Variable(starts_with)
        else:
            self.starts_with = None

    def render(self, context):
        flatpages = FlatPage.objects.fileter(is_enabled=True)#filter(sites__id=settings.SITE_ID)
        # If a prefix was specified, add a filter
        if self.starts_with:
            flatpages = flatpages.filter(
                url__startswith=self.starts_with.resolve(context))
        context[self.context_name] = flatpages
        return ''


def get_flatpages(parser, token):
    """
    Retrieves all flatpage objects available for the current site and
    visible to the specific user (or visible to all users if no user is
    specified). Populates the template context with them in a variable
    whose name is defined by the ``as`` clause.

    An optional argument, ``starts_with``, can be applied to limit the
    returned flatpages to those beginning with a particular base URL.
    This argument can be passed as a variable or a string, as it resolves
    from the template context.

    Syntax::

        {% get_flatpages ['url_starts_with'] as context_name %}

    Example usage::

        {% get_flatpages as flatpages %}
        {% get_flatpages '/about/' as about_pages %}
        {% get_flatpages prefix as about_pages %}
    """
    bits = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of %(tag_name)s "
                       "['url_starts_with'] as context_name" %
                       dict(tag_name=bits[0]))
   # Must have at 3-6 bits in the tag
    if len(bits) >= 3 and len(bits) <= 4:

        # If there's an even number of bits, there's no prefix
        if len(bits) % 2 == 0:
            prefix = bits[1]
        else:
            prefix = None

        # The very last bit must be the context name
        if bits[-2] != 'as':
            raise template.TemplateSyntaxError(syntax_message)
        context_name = bits[-1]

        return FlatpageNode(context_name, starts_with=prefix)
    else:
        raise template.TemplateSyntaxError(syntax_message)

register.tag('get_flatpages', get_flatpages)