import cv2 as cv
import urllib.request
from io import BytesIO
import numpy as np
import random as rng
from sklearn.cluster import KMeans
from skimage.util import img_as_float

def kmeans_fast(features, k, num_iters=100):
    """ Use kmeans algorithm to group features into k clusters.

    This function makes use of numpy functions and broadcasting to speed up the
    first part(cluster assignment) of kmeans algorithm.

    Hints
    - You may find np.repeat and np.argmin useful

    Args:
        features - Array of N features vectors. Each row represents a feature
            vector.
        k - Number of clusters to form.
        num_iters - Maximum number of iterations the algorithm will run.

    Returns:
        assignments - Array representing cluster assignment of each point.
            (e.g. i-th point is assigned to cluster assignments[i])
    """

    N, D = features.shape

    assert N >= k, 'Number of clusters cannot be greater than number of points'

    # Randomly initalize cluster centers
    idxs = np.random.choice(N, size=k, replace=False)
    # idxs = np.floor(np.linspace(0, N-1, k)).astype(int)
    if np.floor(N/2) not in idxs:
        idxs[np.random.choice(len(idxs), size=1, replace=False)] = np.floor(N/2)
    centers = features[idxs]
    assignments = np.zeros(N)

    for n in range(num_iters):
        # Step 2: assign point to closest center
        new_assignments = np.zeros(N)
        distances = np.sqrt(((features - centers[:, np.newaxis])**2).sum(axis=2))
        new_assignments = np.argmin(distances, axis=0)
        
        # Step 3: compute new center of each cluster
        for center_k in range(k):
            cluster_i = features[new_assignments == center_k]
            centers[center_k] = np.mean(cluster_i, axis=0)
            
        # Step 4: check for differences
        if np.sum(new_assignments - assignments) == 0:
            break
        assignments = new_assignments

    return assignments

def image_segmentation(img):
    # First method

    # img = cv.blur(img, (5, 5))
    # gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    # ret, thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    # return thresh

    # Second method (doesn't work at all)
    # kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=np.float32)

    # imgLaplacian = cv.filter2D(img, cv.CV_32F, kernel)
    # sharp = np.float32(img)
    # imgResult = sharp - imgLaplacian
    # # convert back to 8bits gray scale
    # imgResult = np.clip(imgResult, 0, 255)
    # imgResult = imgResult.astype('uint8')
    # imgLaplacian = np.clip(imgLaplacian, 0, 255)
    # imgLaplacian = np.uint8(imgLaplacian)

    # bw = cv.cvtColor(imgResult, cv.COLOR_BGR2GRAY)
    # _, bw = cv.threshold(bw, 40, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)

    # dist = cv.distanceTransform(bw, cv.DIST_L2, 3)
    # cv.normalize(dist, dist, 0, 1.0, cv.NORM_MINMAX)
    # _, dist = cv.threshold(dist, 0.4, 1.0, cv.THRESH_BINARY)

    # kernel1 = np.ones((3,3), dtype=np.uint8)
    # dist = cv.dilate(dist, kernel1)

    # dist_8u = dist.astype('uint8')
    # # Find total markers
    # _, contours, _ = cv.findContours(dist_8u, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # # Create the marker image for the watershed algorithm
    # markers = np.zeros(dist.shape, dtype=np.int32)
    # # Draw the foreground markers
    # for i in range(len(contours)):
    #     cv.drawContours(markers, contours, i, (i+1), -1)

    # imgResult = cv.watershed(imgResult, markers)

    # colors = []
    # for contour in contours:
    #     colors.append((rng.randint(0,256), rng.randint(0,256), rng.randint(0,256)))

    # # Create the result image
    # dst = np.zeros((markers.shape[0], markers.shape[1], 3), dtype=np.uint8)
    # # Fill labeled objects with random colors
    # for i in range(markers.shape[0]):
    #     for j in range(markers.shape[1]):
    #         index = markers[i,j]
    #         if index > 0 and index <= len(contours):
    #             dst[i,j,:] = colors[index-1]

    # return imgResult

    # Third method
    # for i in range(2):
    #     img = cv.blur(img, (5 + i, 5 + i))

    #     Z = img.reshape((-1,3))

    #     # convert to np.float32
    #     Z = np.float32(Z)

    #     # define criteria, number of clusters(K) and apply kmeans()
    #     criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    #     K = int(6 - np.floor(i))
    #     ret,label,center=cv.kmeans(Z,K,None,criteria,10,cv.KMEANS_RANDOM_CENTERS)

    #     # Now convert back into uint8, and make original image
    #     center = np.uint8(center)
    #     res = center[label.flatten()]
    #     res2 = res.reshape((img.shape))

    #     img = res2

    n_k = 25

    # Fourth method
    # img = cv.blur(img, (3, 3))

    normalized_img = img/255

    H, W, C = img.shape
    color = img_as_float(img)
    features = np.zeros((H*W, C+3))
    
    grid = np.dstack(np.mgrid[0:H,0:W])
    grid = 5*(grid - np.mean(grid))/np.std(grid)
    new_img = 1.2*(img - np.mean(img))/np.std(img)
    edges = cv.blur(img, (3, 3))
    edges = cv.Canny(edges, 90, 150)
    edges = cv.blur(edges, (2, 2))
    edges = 0.5*(edges - np.mean(edges))/np.std(edges)
    edges = edges.reshape([edges.shape[0], edges.shape[1], 1])

    new_image = np.dstack((new_img, grid, edges))

    # import pdb
    # pdb.set_trace()

    features = np.reshape(new_image, [H*W, C+3], order='A')

    assignments = kmeans_fast(features, n_k, num_iters=100)

    segments = assignments.reshape((H, W))

    main_cluster = segments[int(H/2), int(W/2)]

    segments[segments == main_cluster] = 255
    segments[segments != 255] = 0
    rgb_segments = np.stack([segments, segments, segments], axis=-1)
    rgb_segments = np.clip(rgb_segments + img, 0, 255)

    segments = segments*(255/(n_k-1))

    return rgb_segments
