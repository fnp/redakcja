import os

from django.conf import settings


def get_image_folders():
    return [fn for fn in os.listdir(settings.IMAGE_DIR) if not fn.startswith('.')]


def get_images_from_folder(folder):
    return ['/media/images/' + folder + '/' + fn for fn 
            in os.listdir(os.path.join(settings.IMAGE_DIR, folder))
            if not fn.startswith('.')]

