#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.  
#
import sys
import os
import shutil
from os.path import splitext, dirname, basename, realpath
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
    

def try_creating(directory):
    try:
        os.mkdir(directory)
    except:
        pass


output_dir = realpath(os.getcwd()) + '/output'
# big_output_dir = output_dir + '/big'
tmp_output_dir = output_dir + '/tmp'

try_creating(output_dir)
# try_creating(big_output_dir)
try_creating(tmp_output_dir)


for file_name in sys.argv[1:]:
    base_name, ext = splitext(file_name)
    try:
        image = Image.open(file_name)
    except IOError, e:
        sys.stderr.write('\nerror:%s:%s\n' % (file_name, e.message))
        continue
    
    # Check ratio
    if ratio(image) > 1:
        images = [crop(image, 0.6), crop(image, 0.6, from_right=True)]
    else:
        images = [image]
    
    for i, image in enumerate(images):
        image_name = '%s.%d.png' % (basename(base_name), i)
        
        # Save files
        small_image = resize(image, 640, 960)
        small_image = small_image.convert('L')
        small_image = ImageOps.autocontrast(small_image, cutoff=85)
        # small_image = small_image.filter(ImageFilter.SHARPEN)
        small_image.save(tmp_output_dir + '/' + image_name)

        os.system('pngnq -n 128 -s 1 -e .png -d "%s" -f "%s"' % (
            output_dir,
            tmp_output_dir + '/' + image_name,
        ))
        os.remove(tmp_output_dir + '/' + image_name)
        
        # big_image = resize(image, 960, 1440)
        # big_image = big_image.convert('L')
        # big_image = big_image.filter(ImageFilter.SHARPEN)
        # big_image.save(tmp_output_dir + '/' + image_name, optimize=True)
        # os.system('pngnq -n 16 -s 1 -e .png -d "%s" -f "%s"' % (
        #     big_output_dir,
        #     tmp_output_dir + '/' + image_name,
        # ))
        # os.remove(tmp_output_dir + '/' + image_name)
        
    sys.stderr.write('.')

shutil.rmtree(tmp_output_dir)
