import cv2
import base64

def image_to_string(image):
	_, buffer = cv2.imencode('.png', image)
	buff = str(base64.b64encode(buffer))[2:-1]
	return buff