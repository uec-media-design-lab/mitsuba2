import cv2
import glob
import os
import numpy as np
import sys

opt_dir = os.path.join("outputs/invert_infloasion", sys.argv[1])

outs = glob.glob(os.path.join(opt_dir, '*/out_0500.png'))
texs = glob.glob(os.path.join(opt_dir, '*/texture_0500.png'))

img = cv2.imread(texs[0])



inwidth, inheight = np.array(img.shape[:2][::-1]).astype(np.int32)
outwidth, outheight = int(inwidth*4), int(inheight*4)

out_data = np.ones((outheight, outwidth, 3), dtype=np.uint8)

for x in range(4):
    for y in range(4):
        img_name = 'crop{}_{}/texture_0500.png'.format(x, y)
        img = cv2.imread(os.path.join(opt_dir, img_name))
        xstart, xend = x*inwidth, (x+1)*inwidth
        ystart, yend = y*inheight, (y+1)*inheight
        out_data[ystart:yend, xstart:xend] += img

        cv2.imshow("img", img)

cv2.imwrite(os.path.join(opt_dir, "merged_tex.png"), out_data)
