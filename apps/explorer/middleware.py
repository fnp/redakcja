import urllib

from django.conf import settings
from django.utils import simplejson

from explorer import models


class EditorSettingsMiddleware(object):
    def process_request(self, request):
        if request.user.is_anonymous():
            return
        cookie_settings = request.COOKIES.get(settings.EDITOR_COOKIE_NAME, '{}')
        
        cookie_settings = simplejson.loads(urllib.unquote(cookie_settings))
        last_update = cookie_settings.get('lastUpdate', 0)
        
        try:
            editor_settings = models.EditorSettings.objects.get(user=request.user)
        except models.EditorSettings.DoesNotExist:
            editor_settings = models.EditorSettings(user=request.user)
            editor_settings.set_settings_value(cookie_settings)
            editor_settings.save()

        # print editor_settings.get_settings_value()['lastUpdate'], '<>', last_update
        if editor_settings.get_settings_value()['lastUpdate'] < last_update:
            print "\n\nZmiana!\n\n"
            editor_settings.set_settings_value(cookie_settings)
            editor_settings.save()

        request.editor_settings = editor_settings


    def process_response(self, request, response):
        if hasattr(request, 'editor_settings'):
            response.set_cookie(settings.EDITOR_COOKIE_NAME,
                urllib.quote(request.editor_settings.settings), max_age=7 * 60 * 60 * 24, path='/')

        return response
