from math import *

def print_time(elapsed_time):
    f, i = modf(elapsed_time)
    h = int(i / 3600)
    m = int((i % 3600) / 60)
    s = int(i - h * 3600 - m * 60)
    ms = f
    print("Rendering time: {}h {}m {}s {:.2f}ms".format(h,m,s,ms))

