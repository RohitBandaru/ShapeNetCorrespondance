import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread
import math
'''
a = np.array([	[1,0,0,0],
				[0,1,0,0],
				[0,0,1,5]])
'''
K = np.array([	[-164.06250213,    0.,           75.        ],
 				[   0.,         -164.06250213,   75.        ],
 				[   0.,            0.,            0.25      ]])
K = K*4

Kinv = np.linalg.inv(K)

def dist_array(path, scale, max_dist):
	print('here')
	image = cv2.imread(path, cv2.IMREAD_UNCHANGED)[:,:,0]
	dist = -(image-1)/scale
	dist[dist == max_dist/scale] = None
	print(np.nanmean(dist))
	return dist

def analyze(imfp):
	meta = np.load(imfp + "_meta.npy")

	phi = meta.item()["phi"]
	theta = meta.item()["theta"]
	max_dist = meta.item()["max_dist"]
	scale = meta.item()["scale"]
	r = meta.item()["r"]
	fp = meta.item()["fp"]

	x = r*math.cos(phi)*math.sin(theta)
	y = r*math.sin(phi)
	z = r*math.cos(phi)*math.cos(theta)

	number = imfp.split("/")[-1]

	'''
	ROTATION MATRIX
	'''
	center = np.array([r*np.cos(phi)*np.sin(theta), r*np.sin(phi), r*np.cos(phi)*np.cos(theta)])
	camera_zaxis = -center / np.linalg.norm(center)
	zaxis = np.array([0,0,1])
	camera_yaxis = zaxis - np.dot(camera_zaxis, zaxis)*camera_zaxis
	camera_yaxis = camera_yaxis / np.linalg.norm(camera_yaxis)
	camera_xaxis = np.cross(camera_yaxis, camera_zaxis)
	camera_xaxis = camera_xaxis / np.linalg.norm(camera_xaxis)
	R = np.zeros((3,3))
	R[:,0] = camera_xaxis
	R[:,1] = camera_yaxis
	R[:,2] = camera_zaxis
	# R1 = np.array([[np.cos(-phi), 0, np.sin(-phi)],[0,1,0],[-np.sin(-phi),0,np.cos(-phi)]])
	# #R2 = np.array([[1,0,0],[0,np.cos(-theta),np.sin(-theta)],[0,-np.sin(-theta),np.cos(-theta)]])
	# I = np.eye(3)
	# I[2,2]=-1
	# #R1 = np.array([[1,0,0],[0, np.cos(phi), np.sin(phi)],[0,-np.sin(phi),np.cos(phi)]])
	# #R1 = np.array([[1,0,0],[0, np.cos(phi), np.sin(phi)],[0,-np.sin(phi),np.cos(phi)]])
	# R2 = np.array([[np.cos(-theta), 0, np.sin(-theta)],[0,1,0],[-np.sin(-theta),0,np.cos(-theta)]])
	# P = np.array([[0,1,0],[0,0,1],[1,0,0]])
	# R = P.dot(R1.dot(R2  .dot(I)))
	print(center)
	print(R)
	print(np.dot(R,R.T))
	#R = R.T
	#rotation_fp = fp + '/{0:03d}'.format(int(number)) + "_rot"

	'''
	LAMBDA
	'''
	# coords is array pf [x,y,1]
	rows = np.arange(600)
	cols = np.arange(600)
	coords = np.zeros((600,600,3))
	coords[..., 0] = rows[:, None]
	coords[..., 1] = cols
	coords[:,:,2] = 1

	a = coords.dot(Kinv.T)

	#print("coords",coords.shape)
	dist = dist_array(imfp+"_depth0001.exr", scale, max_dist)

	lmbda = dist/a[:,:,2]

	c = np.array([0,-5,0]).T
	#c = np.array([-x,-y,-z]).T

	#print('c', c)
	print('phi', phi)
	print('theta', theta)

	# a = Kinv * (x y 1)
	# c = (600,600,3)
	xc = a * lmbda.reshape(600,600,1)

	print(xc.dot(R).shape)
	#xc = np.transpose(xc, axes=(1, 0, 2))
	xc = xc[:,:,[1,0,2]]
	print(c.dot(R).reshape(1,1,3))
	xw = np.zeros((600,600,3))
	for i in range(600):
		for j in range(600):
			xw[i,j,:] = R.dot(xc[i,j,:]) #+ c.dot(R).reshape(1,1,3)
	#xw = xc.dot(R) + c.dot(R).reshape(1,1,3)
	#xw = np.transpose(xw, axes=(1, 0, 2))

	print("top left",xw[136,136,:])
	print("top right",xw[136,463,:])
	print("bottom left",xw[463,136,:])
	print("bottom right",xw[463,463,:])
	print("center",xw[300,300,:])
	np.savez(imfp+'.npz', xw=xw, xc=xc, R=R, theta=theta, phi=phi)


	#plt.imshow(xw[:,:,2])
	#plt.imshow(xw[:,:,2])
	#plt.imshow(dist)
	#plt.show()



imfp = "images/models/cube/000"
analyze(imfp)
imfp = "images/models/cube/001"
analyze(imfp)
imfp = "images/models/cube/002"
analyze(imfp)
imfp = "images/models/cube/003"
analyze(imfp)

#dist_array(imfp+"_depth0001.exr", .2, 10)
#print(corners(imfp2))


'''
camera at (0,0,-5)
top left corner (1,1-1) -> (135, 135)
top right corner (-1,1-1) -> (135, 464)
bottom left corner (1,-1-1) -> (464, 135)
bottom right corner (-1,-1-1) -> (464, 464)
'''


'''
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
png depth map
z   pixel_value
-2  243
-3  218
-4  188
-5  149
-6  89
'''
