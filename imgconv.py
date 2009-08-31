#!/usr/bin/env python
import sys
import os
from os.path import splitext, dirname
from PIL import Image, ImageFilter, ImageEnhance, ImageOps


def resize(image, max_width, max_height):
    """Resize image so it's not wider than max_width and not higher than max_height."""
    width, height = image.size
    ratio = max(1.0, float(width) / max_width, float(height) / max_height)
    new_width, new_height = int(width / ratio), int(height / ratio)
    return image.resize((new_width, new_height), Image.ANTIALIAS)


def crop(image, ratio, from_right=False):
    """Crop image to ratio of current width."""
    width, height = image.size
    new_width = width * ratio
    if from_right:
        bounds = (int(width - new_width), 0, int(width), int(height))
    else:
        bounds = (0, 0, int(new_width), int(height))
    image = image.crop(bounds)
    image.load()
    return image


def ratio(image):
    """Return width to height ratio of image."""
    width, height = image.size
    return float(width) / height
    
    
for file_name in sys.argv[1:]:
    try:
        os.mkdir('output')
    except:
        pass
    base_name, ext = splitext(file_name)
    try:
        image = Image.open(file_name)
    except IOError, e:
        sys.stderr.write('\nerror:%s:%s\n' % (file_name, e.message))
        continue
    
    # Check ratio
    if ratio(image) > 1:
        images = [crop(image, 0.5), crop(image, 0.5, True)]
    else:
        images = [image]
    
    for i, image in enumerate(images):
        image = image.filter(ImageFilter.SHARPEN)
        
        image = image.filter(ImageFilter.MinFilter)
        def convert(i):
            if i > 48:
                return 255
            return i
        image = image.point(convert)
        image = ImageOps.autocontrast(image, cutoff=95)
        image = image.convert('L')
        image = image.filter(ImageFilter.SHARPEN)
        
        # Save files
        small_image = resize(image, 480, 720)
        small_image_file_name = '%s.small.%d.png' % (base_name, i)
        small_image.save(small_image_file_name, optimize=True, bits=6)
        os.system('pngnq -n 8 -e .png -d output -f "%s"' % small_image_file_name)
        os.remove(small_image_file_name)
        
        big_image = resize(image, 960, 1440)
        big_image_file_name = '%s.big.%d.png' % (base_name, i)
        big_image.save(big_image_file_name, optimize=True, bits=6)
        os.system('pngnq -n 8 -e .png -d output -f "%s"' % big_image_file_name)
        os.remove(big_image_file_name)
        
    sys.stderr.write('.')
