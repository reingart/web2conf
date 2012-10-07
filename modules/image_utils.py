#!/usr/bin/env python
# coding: utf8

from PIL import Image, ImageDraw, ImageOps

from cStringIO import StringIO

# Crop and scale image to a given size
# based on http://djangosnippets.org/snippets/224/

def rescale(data, width, height, tmp=None, format="JPEG", force=True):
    """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""
    
    max_width = width
    max_height = height

    input_file = StringIO(data)
    img = Image.open(input_file)
    if not force:
        img.thumbnail((max_width, max_height), Image.ANTIALIAS)
    else:
        src_width, src_height = img.size
        src_ratio = float(src_width) / float(src_height)
        dst_width, dst_height = max_width, max_height
        dst_ratio = float(dst_width) / float(dst_height)
        
        if dst_ratio < src_ratio:
            crop_height = src_height
            crop_width = crop_height * dst_ratio
            x_offset = int(float(src_width - crop_width) / 2.0)
            y_offset = 0
        else:
            crop_width = src_width
            crop_height = crop_width / dst_ratio
            x_offset = 0
            y_offset = int(float(src_height - crop_height) / 3.0)
        img = img.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))
        img = img.resize((dst_width, dst_height), Image.ANTIALIAS)
        
    img.save(tmp, format)
    input_file.close()


def build_qr(data, filename):
    import qrcode
    qr = qrcode.QRCode(
        #version=1,
        #error_correction=qrcode.constants.ERROR_CORRECT_L,
        #box_size=10,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image()
    ##img = qr.make_image(image_factory=image_factory)
    img.save(filename)


def center(source, dest, max_width=165, max_height=61):
    "center the logo to preserve aspect ratio"
   
    # open the original image, create a new one:
    logo = Image.open(source)
    im = Image.new("RGB",(max_width, max_height), (255,255,255))
    # calculate padding
    w, h = logo.size
    box = ((max_width - w) / 2, (max_height - h) / 2)
    # copy logo, use mask as some images are broken
    try:
        im.paste(logo, box, logo)
    except ValueError:
        # alternate method to workaround "bad transparency mask" issue
        # warning: sometimes this doesn't work as expected!
        im = ImageOps.fit(logo, (max_width, max_height), Image.ANTIALIAS)

    im.save(dest)
