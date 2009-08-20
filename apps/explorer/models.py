import os

from django.conf import settings


def get_image_folders():
    return sorted(fn for fn in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR)) if not fn.startswith('.'))


def get_images_from_folder(folder):
    return sorted(settings.MEDIA_URL + settings.IMAGE_DIR + '/' + folder + '/' + fn for fn 
            in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.IMAGE_DIR, folder))
            if not fn.startswith('.'))

