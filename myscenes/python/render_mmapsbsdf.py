import os 
import numpy as np 
import mitsuba
import enoki as ek
import time
from math import *
import sys

mitsuba.set_variant('gpu_rgb')

import mitsuba.render as mr
from mitsuba.core import Bitmap, Struct, Thread, math, Properties, Frame3f, Float, Vector3f, warp
from mitsuba.core.xml import load_file, load_string
from mitsuba.python.util import traverse
from mitsuba.render import BSDF, BSDFContext, BSDFFlags, BSDFSample3f, SurfaceInteraction3f, \
                           register_bsdf, Texture

class MMAPsBSDF(BSDF):
    def __init__(self, props):
        BSDF.__init__(self, props)
        self.m_retro_transmittance = \
            load_string('''<spectrum version='2.2.0' type='srgb' name="reflectance">
                                <rgb name="color" value="1.0, 1.0, 1.0"/>
                            </spectrum>''')
        self.m_flags = BSDFFlags.DeltaReflection
        self.m_components = [self.m_flags]
    
    def sample(self, ctx, si, sample1, sample2, active):
        bs = BSDFSample3f()
        bs.wo = mr.retro_transmit(si.wi)
        bs.pdf = 1
        bs.sampled_type = +BSDFFlags.DeltaTransmission
        bs.sampled_component = 0
        bs.eta = 1

        value = self.m_retro_transmittance.eval(si, active)

        return (bs, ek.select(active, value, 0))

    def eval(self, ctx, si, wo, active):
        return 0
    
    def pdf(self, ctx, si, wo, active):
        return 0

    def to_string(self):
        return "MMAPsBSDF[retro_transmittance = %s]".format(self.m_retro_transmittance.to_string())

# Register MMAPs BSDF such that the XML file loader can instantiate it when loading a scene
register_bsdf("mmapsbsdf", lambda props: MMAPsBSDF(props))

def print_time(elapsed_time):
    f, i = modf(elapsed_time)
    h = int(i / 3600)
    m = int((i % 3600) / 60)
    s = int(i - h * 3600 - m * 60)
    ms = f
    print("Rendering time: {}h {}m {}s {:.2f}ms".format(h, m, s, ms))

xmlname = sys.argv[1]
img_name = sys.argv[2]

filename = "xml/{}.xml".format(xmlname)

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

# Write out rendering as high dynamic range OpenEXR file
film.set_destination_file('outputs/{}.exr'.format(img_name))
film.develop()

# Write out a tonemapped JPG of the same rendering
bmp = film.bitmap(raw=True)
bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write('outputs/{}.jpg'.format(img_name))

# Get linear pixel values as a numpy array for further processing
bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
image_np = np.array(bmp_linear_rgb)
print(image_np.shape)