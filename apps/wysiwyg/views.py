# Create your views here.
from django.views.generic.simple import direct_to_template

def index(request):
    return direct_to_template(request,
        'wysiwyg.html', extra_context={
            'listA': [1,2,3,4],
            'listB': [5,6,7,8],
        })