import os 
import numpy as np
import enoki as ek
import mitsuba
import cv2

mitsuba.set_variant('gpu_rgb')

from mitsuba.core import Bitmap, Struct, Thread, Struct 
from mitsuba.core.xml import load_file
from mitsuba.python.autodiff import render, write_bitmap

def crop_refimg(refbmp, crop_window):
    '''
    - refbmp: Bitmap texture
    - crop_window: Window to crop. ((offset_x, offset_y), (size_x, size_y))
    '''

    np_data = np.array(refbmp)
    (cx, cy), (sx, sy) = crop_window[0], crop_window[1]
    croped_img = np_data[cy:cy+sy, cx:cx+sx]
    return croped_img

imgpath = "img/doraemon.jpg"
bitmap_tmp = Bitmap(imgpath).convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
width, height = bitmap_tmp.size()

step = (int(width/5), int(height/5))
for y in range(0, height, step[1]):
    for x in range(0, width, step[0]):
        crop_window = ((x, y), (step[0], step[1]))
        img = crop_refimg(bitmap_tmp, crop_window) * 255
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite("img/step_debug_{}_{}.jpg".format(x, y), img)