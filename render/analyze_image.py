import cv2
import numpy as np
import matplotlib.pyplot as plt

def analyze(r, theta, phi, fp, scale, max_dist):
	R1 = np.array([[1,0,0],[0,np.cos(phi),np.sin(phi)],[0,-np.sin(phi),np.cos(phi)]])
	R2 = np.array([[np.cos(theta),0,np.sin(theta)],[0,1,0],[-np.sin(theta),0,np.cos(theta)]])
	R = R2.dot(R1)
	print(R)
	rotation_fp = fp + '/{0:03d}'.format(int(i)) + "_rot"
	np.save(rotation_fp, R)



def dist_array(path):
	image = cv2.imread(path, cv2.IMREAD_UNCHANGED)[:,:,0]
	dist = -(image-1)/scale
	dist[dist == max_dist/scale] = None
	#print(np.nanmean(dist))
	return dist

def corners(path):
	# returns coordinates of top two corners
	image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
	#print(np.unique(image.reshape(-1, image.shape[2]), axis=0))
	h, w, c = image.shape
	top_left = True
	top_right = False
	bottom_left = False
	bottom_right = False
	corners = []
	for x in range(h):
		for y in range(w):
			pixel = image[x,y,:]
			if(pixel[0]!=0 and top_left):
				top_left = False
				top_right = True
				corners.append((x,y))
			if(top_right and pixel[0]==0):
				top_right = False
				bottom_left = True
				corners.append((x,y-1))
			if(bottom_left and corners[0][1]==y and pixel[0]==0):
				corners.append((x-1,y))
				bottom_left = False
	return corners

imfp = "images/models/cube/00"+str(4)+"_depth0001.exr"
imfp2 = "images/models/cube/00"+str(4)+".png"
#print(corners(imfp2))

def world_coordinates():
	a = np.array([	[1,0,0,0],
					[0,1,0,0],
					[0,0,1,5]])

	K = np.array([	[-164.06250213,    0.,           75.        ],
	 				[   0.,         -164.06250213,   75.        ],
	 				[   0.,            0.,            0.25      ]])

	Kinv = np.linalg.inv(K)

	rows = np.arange(600)
	cols = np.arange(600)
	coords = np.zeros((600,600,3))
	coords[..., 0] = rows[:, None]
	coords[..., 1] = cols
	coords[:,:,2] = 1
	a = coords.dot(Kinv)

	dist = dist_array("images/models/cube/00"+str(4)+"_depth0001.exr")


	lmbda = dist/a[:,:,2]

	# a = Kinv * (x y 1)
	print(np.nanmean(lmbda))

	c = a * lmbda.reshape(600,600,1)


	R = np.load("images/models/cube/004_rot.npy")
	xw = np.sum(c.dot(R),axis=2) - R.dot(np.array([0,0,5]).T)
	print(xw.shape)
	print(xw[135+5,135+5])
	plt.imshow(xw)
	plt.show()

'''
left = np.array([[1,1,-1,1]]).T
right = np.array([[-1,1,-1,1]]).T

rw = np.array([	[1,-1, 1,-1],
				[1, 1,-1,-1],
				[4, 4, 4, 4]])
cm = np.array([	[135,135,464,465],
				[135,465,135,465],
				[1,  1,  1,  1. ]])
'''


'''
camera at (0,0,-5)
top left corner (1,1-1) -> (135, 135)
top right corner (-1,1-1) -> (135, 464)
bottom left corner (1,-1-1) -> (464, 135)
bottom right corner (-1,-1-1) -> (464, 464)

'''


'''
png depth map
z   pixel_value
-2  243
-3  218
-4  188
-5  149
-6  89
'''