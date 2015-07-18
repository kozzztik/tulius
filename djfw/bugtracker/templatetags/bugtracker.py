from django import template
from functools import update_wrapper
from django.utils.decorators import classonlymethod

register = template.Library()

class BugtrackerUrl(template.Node):
    method_name = ''
    args = None
    
    def __init__(self, method_name, args):
        self.method_name = method_name
        self.args = [template.Variable(var) for var in args]
        
    def render(self, context):
        urlizer = context['urlizer']
        args = [arg.resolve(context) for arg in self.args]
        return getattr(urlizer, self.method_name)(*args)

    @classonlymethod
    def tag(self, method_name, args_count=1):
        def view(parser, token):
            args = token.split_contents()
            tag_name = args.pop(0)
            if len(args) <> args_count:
                msg = '%r tag requires a %d arguments' % (tag_name, args_count)
                raise template.TemplateSyntaxError(msg)
            return self(method_name, args)
        # take name and docstring from class
        update_wrapper(view, self, updated=())
        return view

register.tag("bug_url", BugtrackerUrl.tag('bug'))
register.tag("bug_version_url", BugtrackerUrl.tag('by_version'))
register.tag("bug_main", BugtrackerUrl.tag('bugs_main', args_count=0))
register.tag("bug_by_priority", BugtrackerUrl.tag('by_priority'))
register.tag("bug_by_status", BugtrackerUrl.tag('by_status'))
register.tag("bug_by_component", BugtrackerUrl.tag('by_component'))
register.tag("bug_by_type", BugtrackerUrl.tag('by_type'))
register.tag("bug_by_user", BugtrackerUrl.tag('by_user'))
