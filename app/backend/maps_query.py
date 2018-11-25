import cv2
import urllib.request
from io import BytesIO
import numpy as np

def gmaps_image(location, zoom=19, size=[300,300]):
    location = location.replace(" ", "+")
    image_url = "https://maps.googleapis.com/maps/api/staticmap?center=" + location + "&zoom=" + str(zoom) + "&size=" + str(size[0]) + "x" + str(size[1]) + "&maptype=satellite&key=AIzaSyCMCczdtg3LgNkbp-vEMLkhtNKjMkdifVI"
    requested_url = urllib.request.urlopen(image_url)
    image_array = np.asarray(bytearray(requested_url.read()), dtype=np.uint8)
    img = cv2.imdecode(image_array, -1)
    return img