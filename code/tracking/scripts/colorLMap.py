#!/usr/bin/python
import sys
import cv
from cv import LoadImage, SaveImage, LUT, CreateImage, CreateImageHeader
from array import array


fname = sys.argv[1]
outname = sys.argv[2]
LMap = LoadImage(fname, iscolor=cv.CV_LOAD_IMAGE_GRAYSCALE)

LUT = [
(50,34,22),
(24,247,196),
(33,207,189),
(254,194,127),
(88,115,175),
(158,91,64),
(14,90,2),
(100,156,227),
(243,167,17),
(145,194,184),
(234,171,147),
(220,112,93),
(93,132,163),
(122,4,85),
(75,168,46),
(15,5,108),
(180,125,107),
(157,77,167),
(214,89,73),
(52,183,58),
(54,155,75),
(249,61,187),
(143,57,11),
(246,198,0),
(202,177,251),
(229,115,80),
(159,185,1),
(186,213,229),
(82,47,144),
(140,69,139),
(189,115,117),
(80,57,150) ]


w    = LMap.width
h    = LMap.height


# extract the byte data 
format = "%dB" %(w*h)
data = array('B')
data.fromstring(LMap.tostring())
#data    = unpack(format, LMap.tostring() )

# create the new guy
lutted = array('B', [ x for l in data for x in LUT[l] ] )

imout = CreateImageHeader((w,h),8, 3)
cv.SetData(imout, lutted.tostring())

SaveImage(outname, imout)
print outname
