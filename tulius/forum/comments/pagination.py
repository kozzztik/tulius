from django.template import loader, RequestContext


def get_pagination_context(request, page_num, pages_count, window=4):
    try:
        page_range = range(1, pages_count + 1)
        first = set(page_range[:window])
        last = set(page_range[-window:])
        # Now we look around our current page, making sure that we don't wrap
        # around.
        current_start = page_num - 1 - window
        if current_start < 0:
            current_start = 0
        current_end = page_num - 1 + window
        if current_end < 0:
            current_end = 0
        current = set(page_range[current_start:current_end])
        pages = []
        # If there's no overlap between the first set of pages and the current
        # set of pages, then there's a possible need for elusion.
        if len(first.intersection(current)) == 0:
            first_list = list(first)
            first_list.sort()
            second_list = list(current)
            second_list.sort()
            pages.extend(first_list)
            diff = second_list[0] - first_list[-1]
            # If there is a gap of two, between the last page of the first
            # set and the first page of the current set, then we're missing a
            # page.
            if diff == 2:
                pages.append(second_list[0] - 1)
            # If the difference is just one, then there's nothing to be done,
            # as the pages need no elusion and are correct.
            elif diff == 1:
                pass
            # Otherwise, there's a bigger gap which needs to be signaled for
            # elusion, by pushing a None value to the page list.
            else:
                pages.append(None)
            pages.extend(second_list)
        else:
            unioned = list(first.union(current))
            unioned.sort()
            pages.extend(unioned)
        # If there's no overlap between the current set of pages and the last
        # set of pages, then there's a possible need for elusion.
        if len(current.intersection(last)) == 0:
            second_list = list(last)
            second_list.sort()
            diff = second_list[0] - pages[-1]
            # If there is a gap of two, between the last page of the current
            # set and the first page of the last set, then we're missing a 
            # page.
            if diff == 2:
                pages.append(second_list[0] - 1)
            # If the difference is just one, then there's nothing to be done,
            # as the pages need no elusion and are correct.
            elif diff == 1:
                pass
            # Otherwise, there's a bigger gap which needs to be signaled for
            # elusion, by pushing a None value to the page list.
            else:
                pages.append(None)
            pages.extend(second_list)
        else:
            differenced = list(last.difference(current))
            differenced.sort()
            pages.extend(differenced)
        to_return = {
            'pages': pages,
            'page_num': page_num,
            'previous_page_num': page_num - 1 if page_num > 1 else None,
            'next_page_num': page_num + 1 if pages_count > page_num else None,
            'pages_count': pages_count,
            'is_paginated': pages_count > 1,
        }
        getvars = request.GET.copy()
        if 'page' in getvars:
            del getvars['page']
        if len(getvars.keys()) > 0:
            to_return['getvars'] = "&%s" % getvars.urlencode()
        else:
            to_return['getvars'] = ''
        return to_return
    except KeyError, AttributeError:
        return {}


def get_custom_pagination(request, context, template_name='forum/snippets/pagination.haml'):
    c = RequestContext(request, context)
    t = loader.get_template(template_name)
    return t.render(c)


def get_pagination(request, page_num, pages_count, window=4, template_name='forum/snippets/pagination.haml'):
    context = get_pagination_context(request, page_num, pages_count, window)
    return get_custom_pagination(request, context, template_name)
