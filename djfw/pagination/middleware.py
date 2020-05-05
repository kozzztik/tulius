def get_page(self):
    """
    A function which will be monkeypatched onto the request to get the current
    integer representing the current page.
    """
    try:
        if self.POST:
            p = self.POST['page']
        else:
            p = self.GET['page']
        if p == 'last':
            return 'last'
        return int(p)
    except (KeyError, ValueError, TypeError):
        return 1


class PaginationMiddleware:
    """
    Inserts a variable representing the current page onto the request object if
    it exists in either **GET** or **POST** portions of the request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.page = get_page(request)
        return self.get_response(request)
