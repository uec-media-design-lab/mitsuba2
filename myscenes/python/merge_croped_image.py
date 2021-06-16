import cv2
import glob
import os
import numpy as np
import sys

def heaviside_result(x, threshold):
    '''
    - x : array or numeric object
    - threshold : float value
    '''
    return x * (1 * (x > threshold))

def heaviside_img(img, gray_thres):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = gray * (gray > gray_thres)
    rows, cols = gray.shape

    out_data = np.zeros(img.shape, dtype=np.float32)
    for r in range(rows):
        for c in range(cols):
            out_data[r, c] = img[r, c] if gray[r, c] != 0 else [0, 0, 0]
    return out_data

def imshow(img, window_name="img"):
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

opt_dir = os.path.join("outputs/invert_infloasion", sys.argv[1])

texs = glob.glob(os.path.join(opt_dir, '*/texture_0500.png'))

img = cv2.imread(texs[0])

width, height = img.shape[:2][::-1]

out_data = np.zeros((width, height, 3), dtype=np.float32)

crop_size = (int(width/4), int(height/4))

gray_thres = 50
for x in range(4):
    for y in range(4):
        img_name = 'crop{}_{}/texture_0500.png'.format(x, y)
        img = cv2.imread(os.path.join(opt_dir, img_name))
        out_data += img

cv2.imwrite(os.path.join(opt_dir, "merged_tex.png"), out_data)