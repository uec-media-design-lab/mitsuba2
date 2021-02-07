import os 
import numpy as np
import mitsuba 

mitsuba.set_variant('gpu_rgb')

from mitsuba.core import Bitmap, Struct, Thread 
from mitsuba.core.xml import load_file 

def split_header_format(filename):
    elems = filename.split('.')
    file_format = elems[::-1][0]
    header = '.'.join(elems[0:len(elems)-1])
    return header, file_format

xmlfile = input("XML file that describes the scene: ")

filename = 'xml/{}'.format(xmlfile)
outname = split_header_format(xmlfile)[0]

Thread.thread().file_resolver().append(os.path.dirname(filename))

scene = load_file(filename)
scene.integrator().render(scene, scene.sensors()[0])

film = scene.sensors()[0].film()

film.set_destination_file('outputs/{}.exr'.format(outname))
film.develop()

bmp = film.bitmap(raw=True)
bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write('outputs/{}.jpg'.format(outname))

bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=True)
image_np = np.array(bmp_linear_rgb)
print(image_np.shape)