import os
import numpy as np 
import mitsuba 
import enoki as ek 
import time 
from math import *
import sys

# Custom module
from modules import xml_util as xut
from modules import util as ut

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
        cos_theta_i = Frame3f.cos_theta(si.wi)

        active &= cos_theta_i > 0

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

register_bsdf("mmapsbsdf", lambda props: MMAPsBSDF(props))

xmlname = sys.argv[1]
outpath = os.path.join('outputs', sys.argv[2])
os.makedirs(outpath, exist_ok=True)

filename = 'xml/{}.xml'.format(xmlname)

Thread.thread().file_resolver().append(os.path.dirname(filename))

angle_min, angle_max = -15, 15
dangle = 1/3
current_angle = angle_min 
cam2origin = 100
while current_angle <= angle_max:
    cam_x = sin(radians(current_angle)) * cam2origin
    cam_y = 0
    cam_z = -cos(radians(current_angle)) * cam2origin
    xut.set_perspective(filepath=filename, origin=[cam_x, cam_y, cam_z], target=[0,0,0], fov=40, spp=128)

    scene = load_file(filename)

    start_time = time.time()

    scene.integrator().render(scene, scene.sensors()[0])

    end_time = time.time()
    elapsed_time = end_time - start_time 
    ut.print_time(elapsed_time)

    film = scene.sensors()[0].film()
    film.set_destination_file(os.path.join(outpath, 'angle{:.2f}.exr'.format(current_angle)))
    film.develop()

    bmp = film.bitmap(raw=True)
    bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(os.path.join(outpath, 'angle{:.2f}.jpg'.format(current_angle)))

    current_angle += dangle