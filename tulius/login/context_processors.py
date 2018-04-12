from .forms import ReLoginForm

def relogin(request):
    return {'relogin_form': ReLoginForm(initial={'next_url': request.path}),}