from PIL import Image, ImageOps

import os
from os import listdir
from os.path import isfile, join

files = listdir('./images')
counter = 0

for file in files:

    imagepath = './images/{}'.format(file)

    filename, extension = os.path.splitext(imagepath)

    if(extension != '.jpg'):
        continue

    # open image
    img = Image.open(imagepath)

    #set editing params
    color = "black"
    border = (120, 120, 120, 120)

    #expand, save
    new_img = ImageOps.expand(img, border=border, fill=color)
    new_img.save('./bordered/{}'.format(file))

    counter += 1
    print('{} / {}'.format(counter, len(files)))