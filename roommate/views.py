from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    context = {
        'root': 'home',
        'title':'Roommate'
    }
    return render(request, 'roommate/sample.html',context=context)

def handler404(request):
    response = render_to_response('roommate/404.html', {})
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('roommate/500.html', {})
    response.status_code = 500
    return response