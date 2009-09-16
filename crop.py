#!/usr/bin/env python
import sys
import os
from os.path import splitext, dirname, basename, realpath
from PIL import Image


def crop(image, top=0, right=0, bottom=0, left=0):
    width, height = image.size
    if top < 1:
        top = int(height * top)
    if right < 1:
        right = int(width * right)
    if bottom < 1:
        bottom = int(height * bottom)
    if left < 1:
        left = int(width * left)
    
    bounds = (int(left), int(top), int(width - right), int(height - bottom))
    image = image.crop(bounds)
    image.load()
    return image


output_dir = realpath(os.getcwd()) + '/output'
bounds = [float(i) for i in sys.argv[1].split(':')]

for file_name in sys.argv[2:]:
    base_name, ext = splitext(file_name)
    try:
        image = Image.open(file_name)
    except IOError, e:
        sys.stderr.write('\nerror:%s:%s\n' % (file_name, e.message))
        continue
    
    image = crop(image, *bounds)
    image.save(output_dir + '/' + basename(file_name))