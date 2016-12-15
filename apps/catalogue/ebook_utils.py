# -*- coding: utf-8 -*-
from django.http import HttpResponse


def serve_file(file_path, name, mime_type):
    def read_chunks(f, size=8192):
        chunk = f.read(size)
        while chunk:
            yield chunk
            chunk = f.read(size)

    response = HttpResponse(content_type=mime_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % name
    with open(file_path) as f:
        for chunk in read_chunks(f):
            response.write(chunk)
    return response
