from django.shortcuts import render
from .models import Isbn, IsbnPool


def isbn_list(request):
    return render(request, 'isbn/list.html', {
        'pools': IsbnPool.objects.all(),
        'list': Isbn.objects.all(),
    })
