import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt



def create_segmentation(img):
	gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
	ret, thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV + cv.THRESH_OTSU) #+cv.THRESH_OTSU

	# noise removal
	kernel = np.ones((3,3),np.uint8)
	opening = cv.morphologyEx(thresh,cv.MORPH_OPEN,kernel, iterations = 1)

	# sure background area
	sure_bg = cv.dilate(opening,kernel,iterations=7)

	# Finding sure foreground area
	dist_transform = cv.distanceTransform(opening,cv.DIST_L2,5)
	ret, sure_fg = cv.threshold(dist_transform,0.05*dist_transform.max(),255,0)

	# Finding unknown region
	sure_fg = np.uint8(sure_fg)
	unknown = cv.subtract(sure_bg,sure_fg)

	# inverse the pixel values
	unknown2 = 255 - unknown

	return(unknown2)


def create_contours(img, segmented_img):

	_, contours, _ = cv.findContours(segmented_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

	for cont in contours:
	    
	    # epsilon is the maximum distance between the contour and the approximated contour
	    # epsilon = error_rate * actual_arc_length
	    
	    epsilon = 0.01 * cv.arcLength(cont, True)
	    
	    # use approxPolyDP to approximate the polygon
	    approx = cv.approxPolyDP(cont, epsilon, True)
	    
	    # img2 = cv.drawContours(img2, [approx], 0, (0,0,255), 3)

	    centre = (img.shape[0]/2, img.shape[1]/2)

	valid_contours = []

	for cont in contours:

	    dist = cv.pointPolygonTest(cont,centre,False)
	    if  dist != -1:
	        valid_contours += [cont]

	print("{} contour(s) found".format(len(valid_contours)))

	return(valid_contours)


def calc_surface(img, contours):

	if bool(contours) is False: 
		raise ValueError("No contours")

	if len(contours) > 1: 
		raise ValueError("More than one contours passed")
	
	surface = cv.contourArea(contours[0])
	
	surface = surface / (img.shape[0] * img.shape[1])

	return(surface)


def predict(img):

	val = create_segmentation(img)

	val = create_contours(img, val)

	val = calc_surface(img, val)

	return(val)


if __name__ == "__main__":

	path = "./sample_images/image3.png"

	img = cv.imread(path)

	print(predict(img))

