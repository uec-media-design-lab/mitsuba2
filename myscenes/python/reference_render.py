import os 
import numpy as np 
import mitsuba
import time
from math import *
import sys

mitsuba.set_variant('gpu_rgb')

from mitsuba.core import Bitmap, Struct, Thread 
from mitsuba.core.xml import load_file

import xml_util

def print_time(elapsed_time):
    f, i = modf(elapsed_time)
    h = int(i / 3600)
    m = int((i % 3600) / 60)
    s = int(i - h * 3600 - m * 60)
    ms = f
    print("Rendering time: {}h {}m {}s {:.2f}ms".format(h, m, s, ms))

def out_config(dir, config):
    filepath = os.path.join(dir, 'config.txt')
    with open(filepath, mode="w") as f:
        for k, v in config.items():
            line = k + ' : ' + str(v) + '\n'
            f.write(line)
    f.close()

render_config = {
    'cam2origin': 80,                       # Distance between camera and origin
    'camfov' : 'horizontal, 39.6',          # FOV of camera 
    'lightsource_texture': 'img/uv_brightness1.0.jpg',    # Grid size of checker
    'rect_scale' : 1,                       # Scale of light source
    'scene' : 'infloasion_ref_onlytexture.xml'
}

img_path = sys.argv[1]
outpath = os.path.join('outputs/ref', img_path)
os.makedirs(outpath, exist_ok=True)
out_config(outpath, render_config)

filename = 'xml/{}'.format(render_config['scene'])

cam_origin = [0, 0, 100]
cam_target = [0, 0, 40]
xml_util.set_perspective(filepath=filename, origin=cam_origin, target=cam_target, spp=128)

# Add the scene directory to the FileResolver's search path
Thread.thread().file_resolver().append(os.path.dirname(filename))

# Load the actual scene
scene = load_file(filename)

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

# Write out rendering as high dynamic range OpenEXR file
film.set_destination_file(os.path.join(outpath, 'infloasion_ref.exr'))
film.develop()

# Write out a tonemapped JPG of the same rendering
bmp = film.bitmap(raw=True)
bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(os.path.join(outpath, 'infloasion_ref.jpg'))

# Get linear pixel values as a numpy array for further processing
bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
image_np = np.array(bmp_linear_rgb)
print(image_np.shape)