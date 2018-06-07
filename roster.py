#!/usr/bin/env python3

import cgitb
import sys
import matplotlib; matplotlib.use('agg')
from soccerimg import most_recent_image

cgitb.enable()

img = most_recent_image()

print("Content-type: image/png\n")
sys.stdout.flush()
sys.stdout.buffer.write(img)

#print("Content-type: text/html\n")
#print("<html><h1>hi")
