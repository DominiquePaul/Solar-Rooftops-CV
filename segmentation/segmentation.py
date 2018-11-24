import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt


img = cv.imread('/Users/dominiquepaul/Desktop/Screenshot 2018-11-24 at 14.48.36.png')
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)

plt.imshow(thresh)
