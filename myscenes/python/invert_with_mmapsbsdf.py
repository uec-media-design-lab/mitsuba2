import os 
import numpy as np 
import enoki as ek
import mitsuba 

mitsuba.set_variant('gpu_autodiff_rgb')

import mitsuba.render as mr
from mitsuba.core import Thread, Bitmap, Float, Struct, math, Properties, Frame3f, Float, Vector3f, warp
from mitsuba.core.xml import load_file, load_string
from mitsuba.python.util import traverse 
from mitsuba.python.autodiff import render, write_bitmap, Adam
from mitsuba.render import BSDF, BSDFContext, BSDFFlags, BSDFSample3f, SurfaceInteraction3f, \
                           register_bsdf, Texture
import time 
import os 
import numpy as np 
import sys

import xml_util

class MMAPsBSDF(BSDF):
    def __init__(self, props):
        BSDF.__init__(self, props)
        self.m_retro_transmittance = \
            load_string('''<spectrum version='2.2.0' type='srgb' name="reflectance">
                                <rgb name="color" value="1.0, 1.0, 1.0"/>
                            </spectrum>''')
        self.m_flags = BSDFFlags.DeltaTransmission
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

# Register MMAPs BSDF such that the XML file loader can instantiate it when loading a scene
register_bsdf("mmapsbsdf", lambda props: MMAPsBSDF(props))

def out_config(dir, config):
    filepath = os.path.join(dir, 'config.txt')
    with open(filepath, mode="w") as f:
        for k, v in config.items():
            line = k + ' : ' + str(v) + '\n'
            f.write(line)
    f.close()

render_config = {
    'scene_xml' : 'infloasion_mmapsbsdf.xml',        # The filename of xml file to optimize texture
    'cam2origin': 80,                           # Distance between camera and origin
    'camfov' : 'horizontal, 39.6',              # FOV of camera
    'lightsource_texture': 'img/uv.jpg',      # Light source texture
    'ref': 'ref/uv03/infloasion_ref.exr',     # Scene of reference image include only reference texture directly placed to imaging position. 
    'opt_texture_size': 1.5,                      # The size of light source to optimize is xx times of reference texture.
    'lightsource_shape': 'simple_plane.obj', 
    'mmaps_size' : 30,                          # The size of MMAPs side
    'object' : 'sphere',                      # The filename of transparent object
    'object_transform' : 'translate 0, 0, 40, scale 2.5',
    'ior' : 1.49,                               # Index of refraction of transparent object
    'learning_rate' : 1e-3,                      # Learning rate
    'num_iteration' : 1001,                      # The number of iteration of optimization process
    'mmapsbsdf' : True,
    # 'dielectric' : "ignore reflection"
}

outimg_dir = sys.argv[1]

# Load the Cornell Box
Thread.thread().file_resolver().append('xml')
xmlfilename = os.path.join('xml', render_config['scene_xml'])
scene = load_file(xmlfilename)
width, height = scene.sensors()[0].film().crop_size()

# Load a reference image (no derivatives used yet)
bitmap_ref = Bitmap(os.path.join('outputs', render_config['ref'])).convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
image_ref = np.array(bitmap_ref).flatten()

# Find differentiable scene parameters
params = traverse(scene)
print(params)

opt_param_name = 'textured_lightsource.emitter.radiance.data'
# Make a backup copy
param_res = params['textured_lightsource.emitter.radiance.resolution']
param_ref = Float(params[opt_param_name])

# Discord all parameters except for one we want to differentiate
params.keep([opt_param_name])

# texture_bitmap = Bitmap('img/checker.jpg').convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
# texture_float = Float(texture_bitmap)
# params['textured_lightsource.emitter.radiance.data'] = texture_bitmap
params['textured_lightsource.emitter.radiance.data'] = ek.full(Float, 0.0, len(param_ref))

opt = Adam(params, lr=render_config['learning_rate'])

time_a = time.time()

outpath = os.path.join('outputs/invert_infloasion/', outimg_dir)
os.makedirs(outpath, exist_ok=True)
out_config(outpath, render_config) # Write out config file

losses = np.array([])

film = scene.sensors()[0].film()
crop_size = film.crop_size()

iterations = render_config['num_iteration']
for it in range(iterations):
    # Perform a differentiable rendering of the scene
    image = render(scene, optimizer=opt, unbiased=True, spp=4)
    if it % 10 == 0:
        write_bitmap(os.path.join(outpath, 'out_%04i.png' % it), image, crop_size)
        write_bitmap(os.path.join(outpath, 'texture_%04i.png' % it), params[opt_param_name],
                    (param_res[1], param_res[0]))
    
    # Objective : MSE between 'image' and 'image_ref'
    ob_val = ek.hsum(ek.sqr(image - image_ref)) / len(image)

    # Back-propropagate errors to input parameters
    ek.backward(ob_val)

    # Optimizer : take a gradient step
    opt.step()

    # Compare iterate against ground-truth value
    err_ref = ek.hsum(ek.sqr(param_ref - params[opt_param_name]))
    losses = np.append(losses, err_ref)
    print('Iteration %04i: error=%g' % (it, err_ref[0]), end='\r')

time_b = time.time()

np.savetxt(os.path.join(outpath, 'losses.csv'), losses, delimiter=",")

print()
print('%f ms per iteration' % (((time_b - time_a) * 1000) / iterations))