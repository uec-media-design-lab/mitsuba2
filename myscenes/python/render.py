import os 
import numpy as np 
import mitsuba
import time
from math import *
import sys

mitsuba.set_variant('gpu_rgb')

from mitsuba.core import Bitmap, Struct, Thread 
from mitsuba.core.xml import load_file

def print_time(elapsed_time):
    f, i = modf(elapsed_time)
    h = int(i / 3600)
    m = int((i % 3600) / 60)
    s = int(i - h * 3600 - m * 60)
    ms = f
    print("Rendering time: {}h {}m {}s {:.2f}ms".format(h, m, s, ms))

<<<<<<< HEAD
xmlname = sys.argv[1]
img_name = sys.argv[2]

filename = "xml/{}.xml".format(xmlname)
=======
xmlfile = input("XML file that describes the scene: ")
imgfile = input("Filename of output image file: ")

filename = 'xml/{}.xml'.format(xmlfile)
>>>>>>> 56368d212de5c5a09b7a23fcdafe6c7a54fe1f5b

# Add the scene directory to the FileResolver's search path
Thread.thread().file_resolver().append(os.path.dirname(filename))

# Load the actual scene
scene = load_file(filename)

# For making updating crop work.
# ref: https://github.com/mitsuba-renderer/mitsuba2/issues/336
# film = scene.sensors()[0].film()
# film.set_crop_window((50, 50), (384, 384))
# sensor = scene.sensors()[0]
# sensor.parameters_changed()

# ========== Start time watch ==========
start_time = time.time()

# Call the scene's integrator to render the loaded scene
scene.integrator().render(scene, scene.sensors()[0])

end_time = time.time()
elapsed_time = end_time - start_time 
print_time(elapsed_time)
# ========== End time watch ==========

# After rendering, the rendered data is stored in the file
film = scene.sensors()[0].film()

<<<<<<< HEAD
# Write out rendering as high dynamic range OpenEXR file
film.set_destination_file('outputs/{}.exr'.format(img_name))
=======
film.set_destination_file('outputs/{}.exr'.format(imgfile))
>>>>>>> 56368d212de5c5a09b7a23fcdafe6c7a54fe1f5b
film.develop()

# Write out a tonemapped JPG of the same rendering
bmp = film.bitmap(raw=True)
<<<<<<< HEAD
bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write('outputs/{}.jpg'.format(img_name))
=======
bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write('outputs/{}.jpg'.format(imgfile))
>>>>>>> 56368d212de5c5a09b7a23fcdafe6c7a54fe1f5b

# Get linear pixel values as a numpy array for further processing
bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
image_np = np.array(bmp_linear_rgb)
print(image_np.shape)