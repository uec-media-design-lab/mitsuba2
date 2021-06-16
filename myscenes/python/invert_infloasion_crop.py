# Simple inverse rendering example: render a cornell box reference image, then
# then replace one of the scene parameters and try to recover it using
# differentiable rendering and gradient-based optimization.

import enoki as ek
import mitsuba
mitsuba.set_variant('gpu_autodiff_rgb')

from mitsuba.core import Thread, Bitmap, Float, Struct
from mitsuba.core.xml import load_file
from mitsuba.python.util import traverse
from mitsuba.python.autodiff import render, write_bitmap, Adam
import time
import os 
import numpy as np
import sys

import xml_util

def crop_refimg(refbmp, crop_window):
    '''
    - refbmp: Bitmap texture
    - crop_window: Window to crop. ((offset_x, offset_y), (size_x, size_y))
    '''

    np_data = np.array(refbmp)
    (cx, cy), (sx, sy) = crop_window[0], crop_window[1]
    croped_img = np_data[cy:cy+sy, cx:cx+sx]
    return croped_img

def out_config(dir, config):
    filepath = os.path.join(dir, 'config.txt')
    with open(filepath, mode="w") as f:
        for k, v in config.items():
            line = k + ' : ' + str(v) + '\n'
            f.write(line)
    f.close()

render_config = {
    'scene_xml' : 'infloasion_cube.xml',        # The filename of xml file to optimize texture
    'cam2origin': 70,                           # Distance between camera and origin
    'camfov' : 'horizontal, 39.6',              # FOV of camera
    'lightsource_texture': 'img/uv.jpg',      # Light source texture
    'ref': 'ref/uv_dark_angle02/ref_angle0.exr',     # Scene of reference image include only reference texture directly placed to imaging position. 
    'opt_texture_size': 3,                      # The size of light source to optimize is xx times of reference texture. 
    'mmaps_size' : 30,                          # The size of MMAPs side
    'object' : 'bunny.obj',                      # The filename of transparent object
    'ior' : 1.52,                               # Index of refraction of transparent object
    'learning_rate' : 0.02,                      # Learning rate
    'num_iteration' : 501,                      # The number of iteration of optimization process
}

outimg_dir = sys.argv[1]

# Load the Cornell Box
Thread.thread().file_resolver().append('xml')
xmlfilename = os.path.join('xml', render_config['scene_xml'])
scene = load_file(xmlfilename)
width, height = scene.sensors()[0].film().crop_size()

# Load a reference image (no derivatives used yet)
bitmap_ref = Bitmap(os.path.join('outputs', render_config['ref'])).convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)

crop_step = (4, 4)
size = (int(width/crop_step[0]), int(height/crop_step[1]))
for x in range(crop_step[0]):
    for y in range(crop_step[1]):
        crop_window = ((int(x*size[0]), int(y*size[1])), size)
        image_ref = crop_refimg(bitmap_ref, crop_window).flatten()

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

        outpath = os.path.join('outputs/invert_infloasion/', outimg_dir, "crop{}_{}".format(x, y))
        os.makedirs(outpath, exist_ok=True)
        out_config(outpath, render_config) # Write out config file

        losses = np.array([])

        film = scene.sensors()[0].film()
        film.set_crop_window(crop_window[0], crop_window[1])
        sensor = scene.sensors()[0]
        sensor.parameters_changed()

        iterations = render_config['num_iteration']
        for it in range(iterations):
            # Perform a differentiable rendering of the scene
            image = render(scene, optimizer=opt, unbiased=True, spp=16)
            if it % 10 == 0:
                write_bitmap(os.path.join(outpath, 'out_%04i.png' % it), image, crop_window[1])
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